import httpx
import json
from fastapi.responses import StreamingResponse
from settings import load_settings, load_preset
from chat_common import ChatMessage, find_start_index
from prompt import make_prompt
from payload import make_payload

async def chat_infermaticai(message: ChatMessage):
    settings = load_settings()
    preset = load_preset()
    async def generate():
        async with httpx.AsyncClient() as client:
            wiBefore = ""
            wiAfter = ""
            persona = "Julien is living alone in a luxury mansion."
            user = "Julien"
            start_index = find_start_index(message.system_token_count, message.entries, preset["max_length"] - settings["max_tokens"], user)
            print(f"start_index: {start_index}")
            prompt = make_prompt(user, message.info.name, wiBefore, message.info.description, message.info.personality, message.info.scenario, wiAfter, persona, message.entries, start_index)
            payload = make_payload(prompt, settings, preset)

            async with client.stream(
                "POST",
                "https://api.totalgpt.ai/v1/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings['infermaticAiApiKey']}",
                    "Content-Type": "application/json"
                }
            ) as response:
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail="API request failed")
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            # Send the start_index when stream ends
                            yield f"data: {json.dumps({'start_index': start_index})}\n\n"
                            print(f"sent start_index: {start_index}")
                            break
                        try:
                            json_data = json.loads(data)
                            if text := json_data.get("choices", [{}])[0].get("text"):
                                yield f"data: {json.dumps({'text': text})}\n\n"
                        except json.JSONDecodeError:
                            continue

    return StreamingResponse(generate(), media_type="text/event-stream")