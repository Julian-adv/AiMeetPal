import json
import pathlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()
settings = None

class Settings(BaseModel):
    infermaticAiApiKey: str
    preset: str
    instruct: str
    context: str
    model: str
    checkpoints_folder: str
    checkpoint_name: str

def get_data_path(subpath):
    return str(pathlib.Path(__file__).parent.parent / "data" / subpath)

def load_settings(reload=False):
    global settings
    if settings is None or reload:
        try:
            with open(get_data_path('settings.json'), "r") as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {
                "infermaticAiApiKey": "your_api_key_here",
                "preset": "anthracite-org-magnum-v4-72b-FP8-Dynamic-preset.json",
                "instruct": "anthracite-org-magnum-v4-72b-FP8-Dynamic-instruct.json",
                "context": "anthracite-org-magnum-v4-72b-FP8-Dynamic-context.json",
                "model": "anthracite-org-magnum-v4-72b-FP8-Dynamic",
                "checkpoints_folder": ".",
                "checkpoint_name": ""
            }

    return settings

def load_preset():
    settings = load_settings()
    with open(get_data_path(settings['preset']), "r") as f:
        return json.load(f)

def load_instruct():
    settings = load_settings()
    with open(get_data_path(settings['instruct']), "r") as f:
        return json.load(f)

def load_context():
    settings = load_settings()
    with open(get_data_path(settings['context']), "r") as f:
        return json.load(f)

@router.get("/api/settings")
async def load_settings_api():
    settings = load_settings(reload=True)
    print(settings)
    try:
        return settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/save_settings")
async def save_settings(data: Settings):
    print(data)
    with open(get_data_path('settings.json'), "w") as f:
        json.dump(data.model_dump(), f, indent=2)
    return {"success": True}