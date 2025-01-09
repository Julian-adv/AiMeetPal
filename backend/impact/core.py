import numpy as np
import torch
from impact import utils
from impact.utils import *
from impact import impact_sampling
from collections import namedtuple


SEG = namedtuple("SEG",
                 ['cropped_image', 'cropped_mask', 'confidence', 'crop_region', 'bbox', 'label', 'control_net_wrapper'],
                 defaults=[None])


def enhance_detail(image, model, clip, vae, guide_size, guide_size_for_bbox, max_size, bbox, seed, steps, cfg,
                   sampler_name,
                   scheduler, positive, negative, denoise, noise_mask, force_inpaint,
                   wildcard_opt=None, wildcard_opt_concat_mode=None,
                   detailer_hook=None,
                   refiner_ratio=None, refiner_model=None, refiner_clip=None, refiner_positive=None,
                   refiner_negative=None, control_net_wrapper=None, cycle=1,
                   inpaint_model=False, noise_mask_feather=0, scheduler_func=None):

    if noise_mask is not None:
        noise_mask = utils.tensor_gaussian_blur_mask(noise_mask, noise_mask_feather)
        noise_mask = noise_mask.squeeze(3)

        if noise_mask_feather > 0 and 'denoise_mask_function' not in model.model_options:
            model = nodes_differential_diffusion.DifferentialDiffusion().apply(model)[0]

    if wildcard_opt is not None and wildcard_opt != "":
        model, _, wildcard_positive = wildcards.process_with_loras(wildcard_opt, model, clip)

        if wildcard_opt_concat_mode == "concat":
            positive = nodes.ConditioningConcat().concat(positive, wildcard_positive)[0]
        else:
            positive = wildcard_positive
            positive = [positive[0].copy()]
            if 'pooled_output' in wildcard_positive[0][1]:
                positive[0][1]['pooled_output'] = wildcard_positive[0][1]['pooled_output']
            elif 'pooled_output' in positive[0][1]:
                del positive[0][1]['pooled_output']

    h = image.shape[1]
    w = image.shape[2]

    bbox_h = bbox[3] - bbox[1]
    bbox_w = bbox[2] - bbox[0]

    # Skip processing if the detected bbox is already larger than the guide_size
    if not force_inpaint and bbox_h >= guide_size and bbox_w >= guide_size:
        print(f"Detailer: segment skip (enough big)")
        return None, None

    if guide_size_for_bbox:  # == "bbox"
        # Scale up based on the smaller dimension between width and height.
        upscale = guide_size / min(bbox_w, bbox_h)
    else:
        # for cropped_size
        upscale = guide_size / min(w, h)

    new_w = int(w * upscale)
    new_h = int(h * upscale)

    # safeguard
    if 'aitemplate_keep_loaded' in model.model_options:
        max_size = min(4096, max_size)

    if new_w > max_size or new_h > max_size:
        upscale *= max_size / max(new_w, new_h)
        new_w = int(w * upscale)
        new_h = int(h * upscale)

    if not force_inpaint:
        if upscale <= 1.0:
            print(f"Detailer: segment skip [determined upscale factor={upscale}]")
            return None, None

        if new_w == 0 or new_h == 0:
            print(f"Detailer: segment skip [zero size={new_w, new_h}]")
            return None, None
    else:
        if upscale <= 1.0 or new_w == 0 or new_h == 0:
            print(f"Detailer: force inpaint")
            upscale = 1.0
            new_w = w
            new_h = h

    if detailer_hook is not None:
        new_w, new_h = detailer_hook.touch_scaled_size(new_w, new_h)

    print(f"Detailer: segment upscale for ({bbox_w, bbox_h}) | crop region {w, h} x {upscale} -> {new_w, new_h}")

    # upscale
    upscaled_image = tensor_resize(image, new_w, new_h)

    cnet_pils = None
    if control_net_wrapper is not None:
        positive, negative, cnet_pils = control_net_wrapper.apply(positive, negative, upscaled_image, noise_mask)
        model, cnet_pils2 = control_net_wrapper.doit_ipadapter(model)
        cnet_pils.extend(cnet_pils2)

    # prepare mask
    if noise_mask is not None and inpaint_model:
        imc_encode = nodes.InpaintModelConditioning().encode
        if 'noise_mask' in inspect.signature(imc_encode).parameters:
            positive, negative, latent_image = imc_encode(positive, negative, upscaled_image, vae, mask=noise_mask, noise_mask=True)
        else:
            print(f"[Impact Pack] ComfyUI is an outdated version.")
            positive, negative, latent_image = imc_encode(positive, negative, upscaled_image, vae, noise_mask)
    else:
        latent_image = to_latent_image(upscaled_image, vae)
        if noise_mask is not None:
            latent_image['noise_mask'] = noise_mask

    if detailer_hook is not None:
        latent_image = detailer_hook.post_encode(latent_image)

    refined_latent = latent_image

    # ksampler
    for i in range(0, cycle):
        if detailer_hook is not None:
            if detailer_hook is not None:
                detailer_hook.set_steps((i, cycle))

            refined_latent = detailer_hook.cycle_latent(refined_latent)

            model2, seed2, steps2, cfg2, sampler_name2, scheduler2, positive2, negative2, upscaled_latent2, denoise2 = \
                detailer_hook.pre_ksample(model, seed+i, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise)
            noise, is_touched = detailer_hook.get_custom_noise(seed+i, torch.zeros(latent_image['samples'].size()), is_touched=False)
            if not is_touched:
                noise = None
        else:
            model2, seed2, steps2, cfg2, sampler_name2, scheduler2, positive2, negative2, upscaled_latent2, denoise2 = \
                model, seed + i, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise
            noise = None

        refined_latent = impact_sampling.ksampler_wrapper(model2, seed2, steps2, cfg2, sampler_name2, scheduler2, positive2, negative2,
                                                          refined_latent, denoise2, refiner_ratio, refiner_model, refiner_clip, refiner_positive, refiner_negative,
                                                          noise=noise, scheduler_func=scheduler_func)

    if detailer_hook is not None:
        refined_latent = detailer_hook.pre_decode(refined_latent)

    # non-latent downscale - latent downscale cause bad quality
    try:
        # try to decode image normally
        refined_image = vae.decode_tiled(refined_latent['samples'], tile_x=64, tile_y=64, )
    except Exception as e:
        #usually an out-of-memory exception from the decode, so try a tiled approach
        refined_image = vae.decode_tiled(refined_latent["samples"], tile_x=64, tile_y=64, )

    if detailer_hook is not None:
        refined_image = detailer_hook.post_decode(refined_image)

    # downscale
    refined_image = tensor_resize(refined_image, w, h)

    # prevent mixing of device
    refined_image = refined_image.cpu()

    # don't convert to latent - latent break image
    # preserving pil is much better
    return refined_image, cnet_pils


def segs_scale_match(segs, target_shape):
    h = segs[0][0]
    w = segs[0][1]

    th = target_shape[1]
    tw = target_shape[2]

    if (h == th and w == tw) or h == 0 or w == 0:
        return segs

    rh = th / h
    rw = tw / w

    new_segs = []
    for seg in segs[1]:
        cropped_image = seg.cropped_image
        cropped_mask = seg.cropped_mask
        x1, y1, x2, y2 = seg.crop_region
        bx1, by1, bx2, by2 = seg.bbox

        crop_region = int(x1*rw), int(y1*rw), int(x2*rh), int(y2*rh)
        bbox = int(bx1*rw), int(by1*rw), int(bx2*rh), int(by2*rh)
        new_w = crop_region[2] - crop_region[0]
        new_h = crop_region[3] - crop_region[1]

        if isinstance(cropped_mask, np.ndarray):
            cropped_mask = torch.from_numpy(cropped_mask)

        if isinstance(cropped_mask, torch.Tensor) and len(cropped_mask.shape) == 3:
            cropped_mask = torch.nn.functional.interpolate(cropped_mask.unsqueeze(0), size=(new_h, new_w), mode='bilinear', align_corners=False)
            cropped_mask = cropped_mask.squeeze(0)
        else:
            cropped_mask = torch.nn.functional.interpolate(cropped_mask.unsqueeze(0).unsqueeze(0), size=(new_h, new_w), mode='bilinear', align_corners=False)
            cropped_mask = cropped_mask.squeeze(0).squeeze(0).numpy()

        if cropped_image is not None:
            cropped_image = tensor_resize(cropped_image if isinstance(cropped_image, torch.Tensor) else torch.from_numpy(cropped_image), new_w, new_h)
            cropped_image = cropped_image.numpy()

        new_seg = SEG(cropped_image, cropped_mask, seg.confidence, crop_region, bbox, seg.label, seg.control_net_wrapper)
        new_segs.append(new_seg)

    return (th, tw), new_segs


def segs_to_combined_mask(segs):
    shape = segs[0]
    h = shape[0]
    w = shape[1]

    mask = np.zeros((h, w), dtype=np.uint8)

    for seg in segs[1]:
        cropped_mask = seg.cropped_mask
        crop_region = seg.crop_region
        mask[crop_region[1]:crop_region[3], crop_region[0]:crop_region[2]] |= (cropped_mask * 255).astype(np.uint8)

    return torch.from_numpy(mask.astype(np.float32) / 255.0)

