from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import torch
import random

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # hide tensorflow warnings
from dotenv import load_dotenv
# from openai import OpenAI
from typing import Optional
import shutil
from diffusers import (
    StableDiffusionXLPipeline,
    StableDiffusionXLImg2ImgPipeline,
    AutoencoderKL,
)
from PIL import Image
from impact.face_detailer import FaceDetailer, tensor2pil
from impact.subcore import UltraBBoxDetector
import base64
from io import BytesIO
from ultralytics import YOLO
import comfy.sd
from impact.utils import pil2tensor

# 1girl,maid,large breasts,christian louboutin highheels, garter straps,stockings,collar,kpop idol,long legs,narrow waist,long hair,ass,cameltoe,bent over

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
model_path = f"d:\\ComfyUI_windows_portable\\ComfyUI\\models\\checkpoints\\{model_name}.safetensors"
ckpt_path = f"d:\\ComfyUI_windows_portable\\ComfyUI\\models\\checkpoints\\{model_name}.safetensors"
embedding_path = f"d:\\ComfyUI_windows_portable\\ComfyUI\\models\\embeddings"

# Main pipeline
pipe = StableDiffusionXLPipeline.from_single_file(
    model_path, torch_dtype=torch.float16
).to("cuda")

# Face enhancement pipeline
face_pipe = StableDiffusionXLImg2ImgPipeline.from_single_file(
    model_path, torch_dtype=torch.float16
).to("cuda")

# Get CLIP model from pipeline
clip_model = face_pipe.text_encoder

# Initialize face detection
face_detector = UltraBBoxDetector(YOLO("face_yolov8m.pt"))  # Use the base model

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


class ChatMessage(BaseModel):
    message: str


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
    try:
        # Since actual OpenAI API call is commented out, return a dummy response
        # response = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "user", "content": message.message}
        #     ]
        # )
        # return {"response": response.choices[0].message.content}
        return {"response": f"Echo: {message.message}"}
    except Exception as e:
        import traceback
        print(f"Error occurred: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


check_point = None
clip = None
vae = None
detailer = None


@app.post("/api/generate-image")
async def generate_image(request: ImageGenerationRequest):
    try:
        print(request)
        negative_prompt = request.negative_prompt if request.negative_prompt else ""
        # Generate the initial image
        image = pipe(
            prompt=request.prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            height=request.height,
            width=request.width,
        ).images[0]

        global check_point
        global clip
        global vae
        if not check_point:
            check_point,clip,vae,_ = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=embedding_path)

        # Initialize FaceDetailer and VAE
        global detailer
        if not detailer:
            detailer = FaceDetailer()

        # encode prompts
        positive = encode(clip, request.prompt)
        negative = encode(clip, negative_prompt)

        seed = random.randint(1, 2147483647)  # 1 to 2^31-1 (max 32-bit signed integer)
        # Process image with FaceDetailer
        enhanced_image = detailer.doit(
            pil2tensor(image),
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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
