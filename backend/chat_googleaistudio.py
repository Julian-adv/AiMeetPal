import json
from chat_common import ChatMessage, find_start_index
from settings import load_api_settings, load_preset
from prompt_googleai import make_googleaistudio_prompt
from payload import make_googleaistudio_payload
from stream_post import stream_post


async def chat_googleaistudio(message: ChatMessage):
    settings = load_api_settings()
    preset = load_preset()
    wiBefore = ""
    wiAfter = ""
    persona = "Julien is living alone in a luxury mansion."
    user = "Julien"
    start_index = find_start_index(
        message.system_token_count,
        message.entries,
        preset["maxContext"] - settings["max_tokens"],
        user,
    )
    print(f"start_index: {start_index}")
    payload = make_googleaistudio_prompt(
        user,
        message.info.name,
        wiBefore,
        message.info.description,
        message.info.personality,
        message.info.scenario,
        message.info.mes_example,
        wiAfter,
        persona,
        message.entries,
        start_index,
        preset,
    )
    payload = make_googleaistudio_payload(payload, settings, preset)
    print(json.dumps(payload, indent=2))
    api_key = settings["api_key"]
    return await stream_post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-thinking-exp-01-21:streamGenerateContent?key={api_key}",
        None,
        payload,
        openai=False,
        start_index=start_index,
    )
