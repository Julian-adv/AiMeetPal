import httpx
from fastapi import APIRouter
from settings import load_settings

router = APIRouter()


async def get_model_infermaticai():
    try:
        settings = load_settings()
        with httpx.Client() as client:
            response = client.get(
                "https://api.totalgpt.ai/v1/models",
                headers={
                    "Authorization": f'Bearer {settings["infermaticai"]["api_key"]}'
                },
            )
            if response.status_code == 200:
                result = response.json()
                print(result)
                models = sorted([x["id"]
                                for x in result["data"]], key=str.lower)
                return {"success": True, "models": models}
            else:
                print(response)
                return {"success": False, "message": response.text}
    except Exception as e:
        print(e)
        return {"success": False, "message": str(e)}


async def get_model_openai():
    try:
        settings = load_settings()
        with httpx.Client() as client:
            response = client.get(
                settings["openai"]["custom_url"] + "/models",
                headers={
                    "Authorization": f'Bearer {settings["openai"]["api_key"]}'
                },
            )
            if response.status_code == 200:
                result = response.json()
                print(result)
                models = sorted([x["id"]
                                for x in result["data"]], key=str.lower)
                return {"success": True, "models": models}
            else:
                print(response)
                return {"success": False, "message": response.text}
    except Exception as e:
        print(e)
        return {"success": False, "message": str(e)}


@router.get("/api/models")
async def get_model():
    settings = load_settings()
    if settings["api_type"] == "infermaticai":
        return await get_model_infermaticai()
    elif settings["api_type"] == "openai":
        return await get_model_openai()
