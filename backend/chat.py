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

class ChatMessage(BaseModel):
    entries: List[ChatEntry]

@router.post("/api/chat")
async def chat(message: ChatMessage):
    settings = load_settings()
    preset = load_preset()
    async def generate():
        async with httpx.AsyncClient() as client:
            speaker = 'Stellar'
            wiBefore = ""
            description = """[Stellar's Personality= "loyal", "cheerful", "intelligent", "smart", "wise", "mischievous", "proactive", "young (20 years old)"]
[Stellar's body= "silver-blonde hair", "long straight hair", "turquoise eyes", "long eyelashes", "white teeth", "pink plump glossy lips", "milky white skin", "porcelain-smooth skin", "large breasts (32F cup)", "firm breasts that seem to defy gravity", "long, slender legs", "slender waist (56cm, 22in)", "tight buttocks", "small feet", "long slender fingers", "tall height (175cm, 5'9)"]
[Genre: romance fantasy; Tags: adult; Scenario: {{char}} is working at {{user}}'s mansion as a head maid.]"""
            personality = ""
            scenario = ""
            wiAfter = ""
            persona = "Julien is living alone in a luxury mansion."
            prompt = make_prompt("Julien", "Stellar", wiBefore, description, personality, scenario, wiAfter, persona, message.entries)
            print(prompt)
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
