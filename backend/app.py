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
import cv2
import numpy as np
from ultralytics import YOLO

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

# Initialize face detection
face_detector = YOLO('yolov8n.pt')  # Use the base model

pipe = StableDiffusionXLPipeline.from_single_file(
    "d:\\ComfyUI_windows_portable\\ComfyUI\\models\\checkpoints\\phonyponypepperoni_v4.safetensors",
    torch_dtype=torch.float16
).to("cuda")

face_pipe = StableDiffusionXLImg2ImgPipeline.from_single_file(
    "d:\\ComfyUI_windows_portable\\ComfyUI\\models\\checkpoints\\phonyponypepperoni_v4.safetensors",
    torch_dtype=torch.float16
).to("cuda")

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

def is_face(box, min_size=30):
    """Check if the detected box likely contains a face based on size and position"""
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    
    # Size check
    if w < min_size or h < min_size:
        return False
    
    # Aspect ratio check (faces are usually roughly square)
    aspect_ratio = w / h
    if aspect_ratio < 0.5 or aspect_ratio > 2.0:
        return False
    
    return True

def process_face(image, face_location, padding_factor=1.5):
    """Extract face region with padding and process it"""
    img_h, img_w = image.shape[:2]
    x, y, w, h = face_location
    
    # Add padding
    padding_x = int(w * (padding_factor - 1) / 2)
    padding_y = int(h * (padding_factor - 1) / 2)
    
    # Calculate padded coordinates
    x1 = max(0, x - padding_x)
    y1 = max(0, y - padding_y)
    x2 = min(img_w, x + w + padding_x)
    y2 = min(img_h, y + h + padding_y)
    
    # Extract face region
    face_region = image[y1:y2, x1:x2]
    face_pil = Image.fromarray(face_region)
    
    # Process face with img2img
    enhanced_face = face_pipe(
        prompt="highly detailed face, perfect face, detailed eyes, detailed facial features, high quality, sharp focus",
        negative_prompt="deformed face, ugly face, bad face, blurry, low quality",
        image=face_pil,
        num_inference_steps=20,
        strength=0.4,
        guidance_scale=7.5
    ).images[0]
    
    # Convert back to numpy and resize to original face region size
    enhanced_face_np = np.array(enhanced_face.resize((x2-x1, y2-y1)))
    
    # Create a mask for smooth blending
    mask = np.zeros((y2-y1, x2-x1), dtype=np.float32)
    cv2.ellipse(mask, 
                center=(int((x2-x1)/2), int((y2-y1)/2)),
                axes=(int((x2-x1)/3), int((y2-y1)/3)),
                angle=0, startAngle=0, endAngle=360,
                color=1, thickness=-1)
    mask = cv2.GaussianBlur(mask, (0,0), sigmaX=min(x2-x1, y2-y1)//8)
    mask = np.stack([mask]*3, axis=-1)
    
    # Blend enhanced face with original
    result = image.copy()
    result[y1:y2, x1:x2] = (enhanced_face_np * mask + face_region * (1-mask)).astype(np.uint8)
    
    return result

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
        # Generate the initial image
        image = pipe(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            height=request.height,
            width=request.width
        ).images[0]
        
        # Convert PIL to numpy for face detection
        image_np = np.array(image)
        
        # Detect objects using YOLOv8
        results = face_detector(image_np, conf=0.3, classes=[0])  # class 0 is person
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                # Convert to integers
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                
                if is_face((x1, y1, x2, y2)):
                    # Calculate width and height
                    w = x2 - x1
                    h = y2 - y1
                    
                    # Process face region
                    print("face detected", x1, y1, w, h)
                    image_np = process_face(image_np, (x1, y1, w, h))
        
        # Convert back to PIL
        final_image = Image.fromarray(image_np)
        
        # Convert the image to base64
        image_base64 = image_to_base64(final_image)
        
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
