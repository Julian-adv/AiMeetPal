import json
import pathlib
from fastapi import APIRouter, HTTPException

router = APIRouter()
settings = None

default_settings = {
    "api_type": "openai",
    "infermaticAiApiKey": "your api key",
    "openAiApiKey": "your api key",
    "customUrl": "https://api.kluster.ai/v1",
    "preset": "anthracite-org-magnum-v4-72b-FP8-Dynamic-preset.json",
    "instruct": "anthracite-org-magnum-v4-72b-FP8-Dynamic-instruct.json",
    "context": "anthracite-org-magnum-v4-72b-FP8-Dynamic-context.json",
    "model": "anthracite-org-magnum-v4-72b-FP8-Dynamic",
    "max_tokens": 1024,
    "checkpoints_folder": "../data/checkpoints",
    "checkpoint_name": "",
}

def get_data_path(subpath):
    return str(pathlib.Path(__file__).parent.parent / "data" / subpath)

def load_settings(reload=False):
    global settings
    if settings is None or reload:
        try:
            with open(get_data_path('settings.json'), "r") as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = default_settings

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
    preset = load_preset()
    try:
        return {
            "settings": settings,
            "preset": preset
        }
    except Exception as e:
        print(f"Error loading settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/save_settings")
async def save_settings(data: dict):
    with open(get_data_path('settings.json'), "w") as f:
        json.dump(data, f, indent=2)
    load_settings(reload=True)
    return {"success": True}