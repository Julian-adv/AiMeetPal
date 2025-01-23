from fastapi import HTTPException, APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
import httpx
import json
from settings import load_settings, load_preset
from prompt import make_prompt
from payload import make_payload

router = APIRouter()

class ChatEntry(BaseModel):
    id: int
    speaker: str
    content: str

class CharInfo(BaseModel):
    name: str
    description: str
    personality: str
    scenario: str

class ChatMessage(BaseModel):
    info: CharInfo
    entries: List[ChatEntry]

@router.post("/api/chat")
async def chat(message: ChatMessage):
    settings = load_settings()
    preset = load_preset()
    async def generate():
        async with httpx.AsyncClient() as client:
            wiBefore = ""
            wiAfter = ""
            persona = "Julien is living alone in a luxury mansion."
            prompt = make_prompt("Julien", message.info.name, wiBefore, message.info.description, message.info.personality, message.info.scenario, wiAfter, persona, message.entries)
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
                            break
                        try:
                            json_data = json.loads(data)
                            if text := json_data.get("choices", [{}])[0].get("text"):
                                yield f"data: {json.dumps({'text': text})}\n\n"
                        except json.JSONDecodeError:
                            continue

    return StreamingResponse(generate(), media_type="text/event-stream")
