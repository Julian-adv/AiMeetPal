<script lang="ts">
  import { get_id } from '../lib/util'
  import { StoryEntryState, type ImageEntry, type StoryEntry } from '../types/story'
  import { Popover, Modal, uiHelpers } from 'svelte-5-ui-lib'
  import { Button } from 'svelte-5-ui-lib'
  import { ArrowLeft, ArrowRight, Camera } from 'svelte-heros-v2'

  interface Prop {
    entry: StoryEntry
    disabled?: boolean
    regenerate_image?: () => void
    scale?: number
    landscape?: boolean
  }

  let { entry, disabled = false, regenerate_image, scale = 1, landscape = false }: Prop = $props()
  let popover_id = `scene-image${get_id()}`
  const imageModal = uiHelpers()
  let modalStatus = $state(false)
  const closeModal = imageModal.close
  $effect(() => {
    modalStatus = imageModal.isOpen
  })

  const default_image: ImageEntry = {
    image: null,
    width: landscape ? 1216 : 832,
    height: landscape ? 832 : 1216,
    prompt: '',
    path: '',
  }
  let image = $derived(
    entry.active_image !== undefined ? entry.images[entry.active_image] : default_image
  )
  let prev_class = $derived(
    entry.active_image !== undefined && entry.active_image > 0 ? 'visible' : 'invisible'
  )
  let next_class = $derived(
    entry.active_image !== undefined && entry.active_image < entry.images.length - 1
      ? 'visible'
      : 'invisible'
  )
  let camera_class = $derived(
    entry.state === StoryEntryState.WaitPrompt ||
      entry.state === StoryEntryState.WaitContent ||
      entry.state === StoryEntryState.WaitImage ||
      regenerate_image === undefined
      ? 'invisible'
      : 'visible'
  )
  let image_scale = $derived(image.width > image.height ? 0.61 * scale : 0.45 * scale)
  let show_buttons = $state(false)

  function go_previous() {
    if (entry.active_image !== undefined && entry.active_image > 0) {
      entry.active_image = entry.active_image - 1
    }
  }

  function go_next() {
    if (entry.active_image !== undefined && entry.active_image < entry.images.length - 1) {
      entry.active_image = entry.active_image + 1
    }
  }
</script>

<div
  id={popover_id}
  role="figure"
  class={image.width > image.height ? 'scene-image-wide' : 'scene-image'}
  style="--image-width: {image.width}px; --image-height: {image.height}px; --image-scale: {image_scale}"
  onmouseenter={() => (show_buttons = true)}
  onmouseleave={() => (show_buttons = false)}
>
  <button type="button" class="image-placeholder" onclick={imageModal.toggle} {disabled}>
    {#if entry.state === StoryEntryState.WaitPrompt || entry.state === StoryEntryState.WaitContent}
      <div class="spinner_square"></div>
    {:else if entry.state === StoryEntryState.WaitImage}
      <div class="spinner_circle"></div>
    {/if}
  </button>
  <div
    class="absolute left-1 bottom-1 right-1 flex justify-between z-10 cursor-pointer {show_buttons
      ? ''
      : 'hidden'}"
  >
    <Button
      color="light"
      class="p-1 backdrop-blur bg-white/30 text-neutral-100 hover:bg-white/50 {prev_class}"
      onclick={go_previous}><ArrowLeft size="20" /></Button
    >
    <Button
      color="light"
      class="p-1 backdrop-blur bg-white/30 text-neutral-300 hover:bg-white/50 {camera_class}"
      onclick={regenerate_image}><Camera size="20" /></Button
    >
    <Button
      color="light"
      class="p-1 backdrop-blur bg-white/30 text-neutral-100 hover:bg-white/50 {next_class}"
      onclick={go_next}><ArrowRight size="20" /></Button
    >
  </div>
  {#if image.image}
    <img src={image.image} alt="Scene visualization" />
  {/if}
</div>
{#if image.prompt}
  <Popover class="text-sm p-2 w-[50%] z-20" triggeredBy="#{popover_id}" position="bottom"
    >{image.prompt}</Popover
  >
{/if}
<Modal size="lg" {modalStatus} {closeModal}>
  <div class="flex flex-col items-center justify-center">
    <img src={image.image} alt="Scene visualization" />
  </div>
</Modal>

<style>
  .scene-image {
    position: relative;
    float: left;
    width: calc(var(--image-width) * var(--image-scale));
    height: calc(var(--image-height) * var(--image-scale));
    margin: 0 1rem 0.5rem 0;
    background: theme('colors.zinc.100');
    border-radius: 8px;
    overflow: hidden;
  }

  .scene-image-wide {
    position: relative;
    width: calc(var(--image-width) * var(--image-scale));
    height: calc(var(--image-height) * var(--image-scale));
    float: none;
    margin: 0 auto 0.5rem auto;
    background: theme('colors.zinc.100');
    border-radius: 8px;
    overflow: hidden;
  }

  .scene-image img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
  }

  .scene-image-wide img {
    max-width: 100%;
    height: auto;
    border-radius: 8px;
  }

  .image-placeholder {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    padding: 1rem;
    justify-content: center;
    align-items: end;
    z-index: 1;
    background: transparent;
  }

  .spinner_square {
    width: 32px;
    height: 32px;
    animation: spin 1s linear infinite;
    border-radius: 0;
    border: 4px solid #bfc9eb;
  }

  .spinner_circle {
    width: 32px;
    height: 32px;
    animation: spin 1s linear infinite;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #bfc9eb;
    border-radius: 50%;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>
