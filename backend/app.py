from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
from pydantic import BaseModel
from typing import List, Optional
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
from settings import load_settings, get_data_path, load_preset
from prompt import make_prompt
from payload import make_payload

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
ckpt_path = f"{get_data_path()}/checkpoints/{model_name}.safetensors"
embedding_path = f"{get_data_path()}/embeddings"

# Initialize face detection
face_detector = UltraBBoxDetector(YOLO(f"{get_data_path()}/face_yolov8m.pt"))  # Use the base model

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


class ChatEntry(BaseModel):
    id: int
    speaker: str
    content: str

class ChatMessage(BaseModel):
    entries: List[ChatEntry]

class SceneContent(BaseModel):
    content: str
    prev_image_prompt: str

class ImagePrompt(BaseModel):
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


@app.post("/api/chat")
async def chat(message: ChatMessage):
    settings = load_settings()
    preset = load_preset()
    async def generate():
        async with httpx.AsyncClient() as client:
            speaker = 'Stellar'
            wiBefore = ""
            description = """[Stellar's Personality= "loyal", "cheerful", "intelligent", "smart", "wise", "mischievous", "proactive", "young (20 years old)"]
[Stellar's body= "silver-blonde hair", "long straight hair", "turquoise eyes", "long eyelashes", "white teeth", "pink plump glossy lips", "milky white skin", "porcelain-smooth skin", "large breasts (32F cup)", "firm breasts that seem to defy gravity", "long, slender legs", "slender waist (56cm, 22in)", "tight buttocks", "small feet", "long slender fingers", "tall height (175cm, 5'9)"]
[Genre: romance fantasy; Tags: adult; Scenario: {{char}} is working at {{user}}'s mansion as a head maid.]"""
            personality = ""
            scenario = ""
            wiAfter = ""
            persona = "Julien is living alone in a luxury mansion."
            prompt = make_prompt("Julien", "Stellar", wiBefore, description, personality, scenario, wiAfter, persona, message.entries)
            print(prompt)
            payload = make_payload(prompt, settings, preset)

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


@app.post("/api/scene-to-prompt")
def scene_to_prompt(scene: SceneContent):
    settings = load_settings()
    preset = load_preset()
    try:
        system_prompt = (
            '<|im_start|>system\n' +
            'You are an expert at updating scene descriptions for Stable Diffusion image generation.\n' +
            '\n' +
            'Your task is to maintain and update character appearance and environment descriptions based on the ongoing conversation.\n' +
            '\n' +
            'RULES:\n' +
            '1. Keep consistent base attributes (like hair color, eye color) unless explicitly changed in the scene\n' +
            '2. Update dynamic elements (expressions, poses, clothing details) based on the current scene\n' +
            '3. Maintain environment continuity while updating with new details from the scene\n' +
            '4. Use specific, vivid, and Stable Diffusion-friendly English terms\n' +
            '5. Format output as comma-separated words or short phrases\n' +
            '\n' +
            'REQUIRED OUTPUT FORMAT:\n' +
            'character appearance: [physical attributes, current state, clothing]\n' +
            'environment: [location details, lighting, atmosphere, objects]\n' +
            '<|im_end|>\n' +
            '<|im_start|>user\n' +
            'Update character appearance and environment based on this scene description:\n' +
            scene.prev_image_prompt + '\n\n' +
            'scene description:\n' +
            scene.content +
            '<|im_end|>\n' +
            '<|im_start|>assistant\n' +
            '\n'
        )

        payload = make_payload(system_prompt, settings, preset, stream=False)

        with httpx.Client(timeout=httpx.Timeout(60.0, connect=30.0)) as client:
            print("generating image prompt...")
            print(payload)
            response = client.post(
                "https://api.totalgpt.ai/v1/completions",
                headers={
                    "Authorization": f"Bearer {settings['infermaticAiApiKey']}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            print(response)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"API request failed: {response.text}"
                )
            
            result = response.json()
            prompt = result["choices"][0]["text"].strip()
            assistant_prompt = '<|start_header_id|>assistant<|end_header_id|>\n'
            if prompt.startswith(assistant_prompt):
                prompt = prompt[len(assistant_prompt):]
            print(prompt)
            return ImagePrompt(prompt=prompt)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


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
