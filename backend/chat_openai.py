import httpx
from fastapi.responses import StreamingResponse
from chat_common import ChatMessage
from prompt_openai import make_openai_prompt
from settings import load_api_settings, load_preset
from chat_common import ChatMessage, find_start_index

async def chat_openai(message: ChatMessage):
    settings = load_api_settings()
    preset = load_preset()
    async def generate():
        async with httpx.AsyncClient() as client:
            wiBefore = ""
            wiAfter = ""
            persona = "Julien is living alone in a luxury mansion."
            user = "Julien"
            start_index = find_start_index(message.system_token_count, message.entries, preset["openai_max_context"] - settings["max_tokens"], user)
            print(f"start_index: {start_index}")
            prompt = make_openai_prompt(user, message.info.name, wiBefore, message.info.description, message.info.personality, message.info.scenario, message.info.mes_example, wiAfter, persona, message.entries, start_index, preset)
            print(prompt)
            return
            payload = make_payload(prompt, settings, preset)

            async with client.stream(
                "POST",
                "https://api.totalgpt.ai/v1/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings['api_key']}",
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