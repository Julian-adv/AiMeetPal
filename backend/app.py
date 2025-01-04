from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional
import shutil
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline
import torch
from PIL import Image
import base64
from io import BytesIO

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

pipe = StableDiffusionXLPipeline.from_single_file(
    "d:\\ComfyUI_windows_portable\\ComfyUI\\models\\checkpoints\\phonyponypepperoni_v4.safetensors",
    torch_dtype=torch.float16
).to("cuda")

# Initialize Stable Diffusion pipeline
# model_id = "runwayml/stable-diffusion-v1-5"
# pipe = StableDiffusionPipeline.from_pretrained(model_id)
# if torch.cuda.is_available():
#     pipe = pipe.to("cuda")
# else:
#     pipe = pipe.to("cpu")

UPLOAD_FOLDER = 'uploads'
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

def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-image")
async def generate_image(request: ImageGenerationRequest):
    try:
        print(request)
        # Generate the image
        image = pipe(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            height=request.height,
            width=request.width
        ).images[0]
        
        # Convert the image to base64
        image_base64 = image_to_base64(image)
        
        return {
            "success": True,
            "image": image_base64,
            "prompt": request.prompt
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": "File uploaded successfully", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
