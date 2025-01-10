from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
from pydantic import BaseModel
import json
import os
import random
import base64
from io import BytesIO
from PIL import Image
from impact.face_detailer import FaceDetailer, tensor2pil
from impact.subcore import UltraBBoxDetector
import comfy.sd
from comfyui.nodes import KSampler, EmptyLatentImage, VAEDecodeTiled
import shutil
import uvicorn
from ultralytics import YOLO
from dotenv import load_dotenv
from typing import Optional

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # hide tensorflow warnings
load_dotenv()

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize models
model_name = "phonyponypepperoni_pppv5"
ckpt_path = f"d:\\ComfyUI_windows_portable\\ComfyUI\\models\\checkpoints\\{model_name}.safetensors"
embedding_path = f"d:\\ComfyUI_windows_portable\\ComfyUI\\models\\embeddings"

# Initialize face detection
face_detector = UltraBBoxDetector(YOLO("face_yolov8m.pt"))  # Use the base model

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


class ChatMessage(BaseModel):
    prompt: str


class ImageGenerationRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    num_inference_steps: Optional[int] = 50
    guidance_scale: Optional[float] = 7.5
    height: Optional[int] = 1216
    width: Optional[int] = 832
    face_steps: Optional[int] = 20


def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def encode(clip, text):
    tokens = clip.tokenize(text)
    return (clip.encode_from_tokens_scheduled(tokens), )


settings = None

@app.post("/api/chat")
async def chat(message: ChatMessage):
    global settings
    if settings is None:
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {
                "model": "anthracite-org-magnum-v4-72b-FP8-Dynamic",
                "max_new_tokens": 512,
                "max_tokens": 512,
                "temperature": 1,
                "top_p": 1,
                "typical_p": 1,
                "typical": 1,
                "infermaticAiApiKey": "your_api_key_here"
            }

    async def generate():
        async with httpx.AsyncClient() as client:

            prompt = ('<|start_header_id|>system<|end_header_id|>\n' +
                '\n' +
                'Develop the plot slowly, always stay in character. Describe all actions in full, elaborate, explicit, graphic, and vivid detail. Mention all relevant sensory perceptions. Keep the story immersive and engaging.\n' +
                '\n' +
                '\n' +
                '## Overall plot description:\n' +
                '\n' +
                'Conversation between Stellar and Julien.\n' +
                '\n' +
                '\n' +
                '## Characters:\n' +
                '\n' +
                '### Stellar\n' +
                '\n' +
                '[Stellar\'s Personality= "loyal", "cheerful", "intelligent", "smart", "wise", "mischievous", "proactive", "young (20 years old)"]\n' +
                '[Stellar\'s body= "silver-blonde hair", "long straight hair", "turquoise eyes", "long eyelashes", "white teeth", "pink plump glossy lips", "milky white skin", "porcelain-smooth skin", "large breasts (32F cup)", "firm breasts that seem to defy gravity", "long, slender legs", "slender waist (56cm, 22in)", "tight buttocks", "small feet", "long slender fingers", "tall height (175cm, 5\'9)"]\n' +
                "[Genre: romance fantasy; Tags: adult; Scenario: Stellar is working at Julien's mansion as a head maid.]\n" +
                '\n' +
                '### Julien\n' +
                '\n' +
                'Julien is living alone in a luxury mansion.\n' +
                '\n' +
                'The first floor of the mansion includes the master bedroom, master bathroom, living room, kitchen, family room, and study. On the second floor, there are rooms for the maids.<|eot_id|>\n' +
                '<|start_header_id|>user<|end_header_id|>\n' +
                '\n' +
                'Start the role-play between Stellar and Julien.\n' +
                '<|eot_id|>\n' +
                '<|start_header_id|>writer character: Stellar<|end_header_id|>\n' +
                '\n' +
                'Good morning. Master. Jessica, your new maid candidate, has arrived and is waiting for you. Shall I bring her here?<|eot_id|>\n' +
                '<|start_header_id|>writer character: Julien<|end_header_id|>\n' +
                '\n' +
                f'{message.prompt}<|eot_id|>\n')

            payload = {
                "prompt": prompt,
                "model": settings["model"],
                "max_new_tokens": settings["max_new_tokens"],
                "max_tokens": settings["max_tokens"],
                "temperature": settings["temperature"],
                "top_p": settings["top_p"],
                "typical_p": settings["typical_p"],
                "typical": settings["typical"],
                "sampler_seed": -1,
                "min_p": 0.02,
                "repetition_penalty": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "top_k": -1,
                "skew": 0,
                "min_tokens": 0,
                "add_bos_token": True,
                "smoothing_factor": 0,
                "smoothing_curve": 1,
                "dry_allowed_length": 2,
                "dry_multiplier": 0.75,
                "dry_base": 1.75,
                "dry_sequence_breakers": '["\\n",":","\\"","*"]',
                "dry_penalty_last_n": 0,
                "max_tokens_second": 0,
                "stopping_strings": [
                    "\nJulien:",
                    "\nStellar:",
                    "<|eot_id|>"
                ],
                "stop": [
                    "\nJulien:",
                    "\nStellar:",
                    "<|eot_id|>"
                ],
                "truncation_length": 8192,
                "ban_eos_token": False,
                "skip_special_tokens": True,
                "top_a": 0,
                "tfs": 1,
                "mirostat_mode": 0,
                "mirostat_tau": 5,
                "mirostat_eta": 0.1,
                "custom_token_bans": "",
                "banned_strings": [],
                "api_type": "infermaticai",
                "api_server": "https://api.totalgpt.ai",
                "xtc_threshold": 0.1,
                "xtc_probability": 0.5,
                "nsigma": 0,
                "n": 1,
                "ignore_eos": False,
                "spaces_between_special_tokens": True,
                "stream": True
            }

            async with client.stream(
                "POST",
                "https://api.totalgpt.ai/v1/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings['infermaticAiApiKey']}",
                    "Content-Type": "application/json"
                }
            ) as response:
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail="API request failed")
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            json_data = json.loads(data)
                            if text := json_data.get("choices", [{}])[0].get("text"):
                                yield f"data: {json.dumps({'text': text})}\n\n"
                        except json.JSONDecodeError:
                            continue

    return StreamingResponse(generate(), media_type="text/event-stream")


check_point = None
clip = None
vae = None
empty_latent_image = None
ksampler = None
vae_decoder = None
detailer = None

@app.post("/api/generate-image")
async def generate_image(request: ImageGenerationRequest):
    try:
        print(request)
        negative_prompt = request.negative_prompt if request.negative_prompt else ""

        global check_point
        global clip
        global vae
        if not check_point:
            check_point,clip,vae,_ = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=embedding_path)

        global empty_latent_image
        if not empty_latent_image:
            empty_latent_image = EmptyLatentImage()

        global ksampler
        if not ksampler:
            ksampler = KSampler()

        global vae_decoder
        if not vae_decoder:
            vae_decoder = VAEDecodeTiled()

        global detailer
        if not detailer:
            detailer = FaceDetailer()

        # encode prompts
        positive = encode(clip, request.prompt)
        negative = encode(clip, negative_prompt)

        seed = random.randint(1, 2147483647)  # 1 to 2^31-1 (max 32-bit signed integer)

        latent_image = empty_latent_image.generate(request.width, request.height)
        latent_image = ksampler.sample(check_point, seed, 50, 4.5, "dpmpp_2m_sde", "karras", positive[0], negative[0], latent_image[0], denoise=1.0)
        vae_decoded_image = vae_decoder.decode(vae, latent_image[0], 512)
        # Process image with FaceDetailer
        enhanced_image = detailer.doit(
            vae_decoded_image[0],
            check_point,
            clip,
            vae,
            512.0,
            True,
            768.0,
            seed,
            request.face_steps,
            4.5,
            "euler",
            "normal",
            positive[0],
            negative[0],
            0.5,
            5,
            True,
            False,
            0.5,
            10,
            3.0,
            "center-1",
            0,
            0.93,
            0,
            0.7,
            "False",
            10,
            face_detector,
            None,
        )

        # Convert the image to base64
        enhanced_img = tensor2pil(enhanced_image[0])
        image_base64 = image_to_base64(enhanced_img)

        return {"success": True, "image": image_base64, "prompt": request.prompt}
    except Exception as e:
        import traceback
        print(f"Error occurred: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": "File uploaded successfully", "filename": file.filename}
    except Exception as e:
        import traceback
        print(f"Error occurred: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
