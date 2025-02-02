import json
import pathlib
from fastapi import APIRouter, HTTPException

router = APIRouter()
settings = None


def get_data_path(subpath):
    return str(pathlib.Path(__file__).parent.parent / "data" / subpath)


def load_settings(reload=False):
    global settings
    if settings is None or reload:
        try:
            with open(get_data_path('settings.json'), "r") as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {}

    return settings


def load_api_settings():
    settings = load_settings()
    if settings['api_type'] == 'infermaticai':
        return settings['infermaticai']
    elif settings['api_type'] == 'openai':
        return settings['openai']


def load_api_settings_for(api: str) -> dict:
    settings = load_settings()
    return settings[api]


def load_preset():
    settings = load_settings()
    if settings['api_type'] == 'infermaticai':
        path = get_data_path(settings['infermaticai']['preset'])
    elif settings['api_type'] == 'openai':
        path = get_data_path(settings['openai']['preset'])
    with open(path, "r") as f:
        return json.load(f)


def load_preset_for(api: str) -> dict:
    if api == 'infermaticai':
        path = get_data_path(settings['infermaticai']['preset'])
    elif api == 'openai':
        path = get_data_path(settings['openai']['preset'])
    with open(path, "r") as f:
        return json.load(f)


def load_instruct():
    settings = load_settings()
    if settings['api_type'] == 'infermaticai':
        path = get_data_path(settings['infermaticai']['instruct'])
        with open(path, "r") as f:
            return json.load(f)
    return {}


def load_context():
    settings = load_settings()
    if settings['api_type'] == 'infermaticai':
        path = get_data_path(settings['infermaticai']['context'])
        with open(path, "r") as f:
            return json.load(f)
    return {}


@router.get("/api/settings")
async def load_settings_api():
    settings = load_settings(reload=True)
    try:
        return {
            "settings": settings,
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
