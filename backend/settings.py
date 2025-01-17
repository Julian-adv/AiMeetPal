import json
import pathlib

settings = None

def get_data_path(subpath):
    return str(pathlib.Path(__file__).parent.parent / "data" / subpath)

def load_settings():
    global settings
    if settings is None:
        try:
            with open(get_data_path('settings.json'), "r") as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {
                "infermaticAiApiKey": "your_api_key_here",
                "preset": "anthracite-org-magnum-v4-72b-FP8-Dynamic-preset.json",
                "instruct": "anthracite-org-magnum-v4-72b-FP8-Dynamic-instruct.json",
                "context": "anthracite-org-magnum-v4-72b-FP8-Dynamic-context.json"
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

