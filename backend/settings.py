import json

settings = None

def load_settings():
    global settings
    if settings is None:
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
        except FileNotFoundError:
            settings = {
                "model": "anthracite-org-magnum-v4-72b-FP8-Dynamic",
                "max_new_tokens": 512,
                "max_tokens": 512,
                "temperature": 1,
                "top_p": 1,
                "typical_p": 1,
                "typical": 1,
                "infermaticAiApiKey": "your_api_key_here"
            }

    return settings