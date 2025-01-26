from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from dotenv import load_dotenv
from character import router as characters_router
from chat import router as chat_router
from image_prompt import router as image_prompt_router
from generate_image import router as generate_image_router
from files import router as files_router
from settings import router as settings_router
from session import router as session_router
from tokenizer import router as tokenizer_router

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # hide tensorflow warnings
load_dotenv()

app = FastAPI()
app.mount("/data", StaticFiles(directory="../data"), name="data")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(image_prompt_router)
app.include_router(generate_image_router)
app.include_router(characters_router)
app.include_router(files_router)
app.include_router(settings_router)
app.include_router(session_router)
app.include_router(tokenizer_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
