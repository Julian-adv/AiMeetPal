from fastapi import APIRouter
from pydantic import BaseModel
import httpx
from settings import load_settings
from chat import ChatMessage
from prompt import make_prompt

router = APIRouter()

class Tokenize(BaseModel):
    text: str

@router.post("/api/count-tokens")
async def count_tokens(message: ChatMessage):
    try:
        settings = load_settings()
        wiBefore = ""
        wiAfter = ""
        persona = "Julien is living alone in a luxury mansion."
        prompt = make_prompt("Julien", message.info.name, wiBefore, message.info.description, message.info.personality, message.info.scenario, wiAfter, persona, message.entries)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.totalgpt.ai/utils/token_counter",
                json={
                    "model": settings["model"],
                    "prompt": prompt
                },
                headers={
                    "Authorization": f"Bearer {settings['infermaticAiApiKey']}",
                    "Content-Type": "application/json"
                }
            )
            result = response.json()
            print(result)
            return {
                "success": True,
                "total_tokens": result["total_tokens"]
            }
                
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return {"success": False, "message": str(e)}