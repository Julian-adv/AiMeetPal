import json
import httpx
from fastapi import HTTPException
from fastapi.responses import StreamingResponse


async def stream_post(url: str, api_key: str, payload: dict, openai: bool = True, start_index: int = 0):
    async def generate():
        async with httpx.AsyncClient() as client:

            max_retries = 3
            retry_count = 0

            while retry_count < max_retries:
                try:
                    async with client.stream(
                        "POST",
                        url,
                        headers={
                            "Authorization": f"Bearer {api_key}",
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
                                    if openai:
                                        text = choices[0].get(
                                            "delta", {}).get("content")
                                        if text:
                                            yield f"data: {json.dumps({'text': text})}\n\n"
                                    else:
                                        text = choices[0].get("text")
                                        if text:
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
                    print(
                        f"Timeout occurred. Retrying... ({retry_count}/{max_retries})")
                    yield f"data: {json.dumps({'reset': True})}\n\n"
                    continue
                break

    return StreamingResponse(generate(), media_type="text/event-stream")
