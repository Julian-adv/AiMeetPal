from fastapi import APIRouter
from settings import load_settings
from chat_infermaticai import chat_infermaticai
from chat_openai import chat_openai
from chat_common import ChatMessage

router = APIRouter()


@router.post("/api/chat")
async def chat(message: ChatMessage):
    settings = load_settings()
    if settings["api_type"] == "infermaticai":
        return await chat_infermaticai(message)
    elif settings["api_type"] == "openai":
        return await chat_openai(message)
