from fastapi import APIRouter
from pydantic import BaseModel
import httpx
from settings import load_api_settings
from chat_common import ChatEntry, CharInfo
from prompt import make_prompt, make_prompt_single

router = APIRouter()

class TokenMessage(BaseModel):
    system_prompt: bool
    info: CharInfo
    entry: ChatEntry


@router.post("/api/count-tokens")
async def count_tokens(message: TokenMessage):
    try:
        settings = load_api_settings()
        wiBefore = ""
        wiAfter = ""
        persona = "Julien is living alone in a luxury mansion."
        if message.system_prompt:
            prompt = make_prompt("Julien", message.info.name, wiBefore, message.info.description, message.info.personality, message.info.scenario, wiAfter, persona, [message.entry], 0)
        else:
            prompt = make_prompt_single("Julien", message.entry)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.totalgpt.ai/utils/token_counter",
                json={
                    "model": settings["model"],
                    "prompt": prompt
                },
                headers={
                    "Authorization": f"Bearer {settings['api_key']}",
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