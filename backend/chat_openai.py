from prompt_openai import make_openai_prompt
from settings import load_api_settings, load_preset
from chat_common import ChatMessage, find_start_index
from payload import make_openai_payload
from stream_post import stream_post


async def chat_openai(message: ChatMessage):
    settings = load_api_settings()
    preset = load_preset()
    wiBefore = ""
    wiAfter = ""
    persona = "Julien is living alone in a luxury mansion."
    user = "Julien"
    start_index = find_start_index(
        message.system_token_count,
        message.entries,
        preset["openai_max_context"] - settings["max_tokens"],
        user,
    )
    print(f"start_index: {start_index}")
    messages = make_openai_prompt(
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
    payload = make_openai_payload(messages, settings, preset)
    return await stream_post(settings["custom_url"] + "/chat/completions", settings["api_key"], payload, start_index)
