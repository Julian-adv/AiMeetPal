from fastapi import APIRouter
from settings import load_settings
import os
from pydantic import BaseModel

router = APIRouter()

class CheckpointSettings(BaseModel):
    folder: str

@router.get("/api/checkpoints")
async def get_checkpoints():
    settings = load_settings()
    checkpoint_folder = settings.get("checkpoint_folder", "checkpoints")
    if not checkpoint_folder:
        return []
    
    try:
        if not os.path.exists(checkpoint_folder):
            return []
        files = os.listdir(checkpoint_folder)
        return [f for f in files if os.path.isfile(os.path.join(checkpoint_folder, f))]
    except Exception as e:
        print(f"Error reading checkpoints directory: {e}")
        return []