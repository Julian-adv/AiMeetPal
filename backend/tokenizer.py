from fastapi import APIRouter
from pydantic import BaseModel
import httpx
from settings import load_api_settings, load_settings, load_preset
from chat_common import ChatEntry, CharInfo
from prompt import make_prompt, make_prompt_single
from prompt_openai import make_openai_prompt
import transformers

router = APIRouter()

# Initialize tokenizer globally
chat_tokenizer_dir = "./deepseek_v3_tokenizer/"
_tokenizer = None


def get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = transformers.AutoTokenizer.from_pretrained(chat_tokenizer_dir, trust_remote_code=True)
    return _tokenizer


class TokenMessage(BaseModel):
    system_prompt: bool
    info: CharInfo
    entry: ChatEntry


async def count_tokens_infermaticai(message: TokenMessage):
    try:
        settings = load_api_settings()
        wiBefore = ""
        wiAfter = ""
        persona = "Julien is living alone in a luxury mansion."
        if message.system_prompt:
            prompt = make_prompt(
                "Julien",
                message.info.name,
                wiBefore,
                message.info.description,
                message.info.personality,
                message.info.scenario,
                wiAfter,
                persona,
                [message.entry],
                0,
            )
        else:
            prompt = make_prompt_single("Julien", message.entry)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.totalgpt.ai/utils/token_counter",
                json={"model": settings["model"], "prompt": prompt},
                headers={
                    "Authorization": f"Bearer {settings['api_key']}",
                    "Content-Type": "application/json",
                },
            )
            result = response.json()
            print(result)
            return {"success": True, "total_tokens": result["total_tokens"]}

    except Exception as e:
        print(f"Error counting tokens: {e}")
        return {"success": False, "message": str(e)}


async def count_tokens_openai(message: TokenMessage):
    try:
        tokenizer = get_tokenizer()
        if message.system_prompt:
            preset = load_preset()
            persona = "Julien is living alone in a luxury mansion."
            messages = make_openai_prompt(
                "Julien",
                message.info.name,
                "",
                message.info.description,
                message.info.personality,
                message.info.scenario,
                message.info.mes_example,
                "",
                persona,
                [],
                0,
                preset,
            )
            total_tokens = 0
            for msg in messages:
                tokens = tokenizer.encode(msg["content"])
                total_tokens += len(tokens)
        else:
            tokens = tokenizer.encode(message.entry.content)
            total_tokens = len(tokens)
        return {"success": True, "total_tokens": total_tokens}
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return {"success": False, "message": str(e)}


async def count_tokens_googleaistudio(message: TokenMessage):
    try:
        tokenizer = get_tokenizer()
        if message.system_prompt:
            preset = load_preset()
            persona = "Julien is living alone in a luxury mansion."
            messages = make_openai_prompt(
                "Julien",
                message.info.name,
                "",
                message.info.description,
                message.info.personality,
                message.info.scenario,
                message.info.mes_example,
                "",
                persona,
                [],
                0,
                preset,
            )
            total_tokens = 0
            for msg in messages:
                tokens = tokenizer.encode(msg["content"])
                total_tokens += len(tokens)
        else:
            tokens = tokenizer.encode(message.entry.content)
            total_tokens = len(tokens)
        return {"success": True, "total_tokens": total_tokens}
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return {"success": False, "message": str(e)}


@router.post("/api/count-tokens")
async def count_tokens(message: TokenMessage):
    settings = load_settings()
    if settings["api_type"] == "infermaticai":
        return await count_tokens_infermaticai(message)
    elif settings["api_type"] == "openai":
        return await count_tokens_openai(message)
    elif settings["api_type"] == "googleaistudio":
        return await count_tokens_googleaistudio(message)
