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
    token_count: int | None = None

class CharInfo(BaseModel):
    name: str
    description: str
    personality: str
    scenario: str

class ChatMessage(BaseModel):
    system_token_count: int
    info: CharInfo
    entries: List[ChatEntry]

def find_start_index(system_token_count: int, entries: List[ChatEntry], max_token_count: int, user: str) -> int:
    try:
        total_tokens = system_token_count
        for i in range(len(entries) - 1, -1, -1):
            entry = entries[i]
            if entry.token_count is not None:
                if total_tokens + entry.token_count > max_token_count:
                    # Find first non-user entry from i + 1
                    for j in range(i + 1, len(entries)):
                        if entries[j].speaker != user:
                            return j
                    return len(entries) - 1  # If no non-user entry found, return end of list
                total_tokens += entry.token_count
            
        return 0
    except Exception as e:
        print(f"Error finding start index: {e}")
        return 0


@router.post("/api/chat")
async def chat(message: ChatMessage):
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
