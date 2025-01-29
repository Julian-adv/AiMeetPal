import httpx
import json
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from chat_common import ChatMessage
from prompt_openai import make_openai_prompt
from settings import load_api_settings, load_preset
from chat_common import ChatMessage, find_start_index
from payload import make_openai_payload


async def chat_openai(message: ChatMessage):
    settings = load_api_settings()
    preset = load_preset()

    async def generate():
        async with httpx.AsyncClient() as client:
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

            max_retries = 3
            retry_count = 0

            while retry_count < max_retries:
                try:
                    async with client.stream(
                        "POST",
                        f"{settings['custom_url']}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings['api_key']}",
                            "Content-Type": "application/json",
                        },
                        json=payload,
                        timeout=60.0,
                    ) as response:
                        print(f"response: {response}")
                        if response.status_code != 200:
                            raise HTTPException(
                                status_code=response.status_code,
                                detail="API request failed",
                            )

                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data = line[6:]
                                if data == "[DONE]":
                                    # Send the start_index when stream ends
                                    yield f"data: {json.dumps({'start_index': start_index})}\n\n"
                                    break
                                try:
                                    json_data = json.loads(data)
                                    choices = json_data.get("choices")
                                    if len(choices) == 0:
                                        continue
                                    if (
                                        text := choices[0]
                                        .get("delta", {})
                                        .get("content")
                                    ):
                                        yield f"data: {json.dumps({'text': text})}\n\n"
                                except json.JSONDecodeError:
                                    continue
                except httpx.TimeoutException as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        raise HTTPException(
                            status_code=504,
                            detail=f"Timeout after {max_retries} retries: {str(e)}",
                        )
                    print(f"Timeout occurred. Retrying... ({retry_count}/{max_retries})")
                    continue
                break

    return StreamingResponse(generate(), media_type="text/event-stream")
