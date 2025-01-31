from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
import httpx
from settings import load_api_settings, load_preset, load_settings
from payload import make_payload, make_openai_payload
from stream_post import stream_post

router = APIRouter()


class SceneContent(BaseModel):
    content: str
    prev_image_prompt: str


class ImagePrompt(BaseModel):
    prompt: str


async def scene_to_prompt_infermaticai(scene: SceneContent):
    settings = load_api_settings()
    preset = load_preset()
    try:
        system_prompt = (
            '<|im_start|>system\n' +
            'You are an expert at updating scene descriptions to create images using the Stable Diffusion model.\n' +
            '\n' +
            'Your job is to maintain and update character appearances and environmental descriptions based on ongoing dialogue.\n' +
            '\n' +
            'RULES:\n' +
            '1. Keep basic attributes (e.g., hair color, eye color) consistent unless explicitly changed in the scene.\n' +
            '2. Update dynamic elements (facial expressions, poses, clothing details) based on the current scene.\n' +
            '3. Maintain the continuity of the environment while updating with new details in the scene.\n' +
            '4. Use specific, clear, stable, spread-friendly English terminology.\n' +
            '5. Format output into comma-separated words or short phrases.\n' +
            '6. Choose appropriate camera angle for the image (e.g., wide shot, full body shot, close-up).\n' +
            '7. Select the appropriate image format (e.g. landscape/portrait).\n' +
            '\n' +
            'Required Output Format:\n' +
            'Character Appearance: [physical characteristics, current state, clothing],\n' +
            'Environment: [location details, lighting, atmosphere, objects],\n' +
            '[angle, shot],\n' +
            'Format: landscape/portrait\n' +
            '<|im_end|>\n' +
            '<|im_start|>user\n' +
            'The current appearance and environment:\n' +
            scene.prev_image_prompt + '\n' +
            '\n' +
            'Update the character\'s appearance and environment above based on the following scene description:\n' +
            scene.content +
            '<|im_end|>\n' +
            '<|im_start|>assistant\n' +
            '\n'
        )

        payload = make_payload(system_prompt, settings, preset, stream=False)

        with httpx.Client(timeout=httpx.Timeout(60.0, connect=30.0)) as client:
            print("generating image prompt with infermaticai...")
            print(f"prev_image_prompt: {scene.prev_image_prompt}")
            print(f"content: {scene.content}")
            response = client.post(
                "https://api.totalgpt.ai/v1/completions",
                headers={
                    "Authorization": f"Bearer {settings['api_key']}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            print(response)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"API request failed: {response.text}"
                )

            result = response.json()
            prompt = result["choices"][0]["text"].strip()
            print(prompt)
            return ImagePrompt(prompt=prompt)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


async def scene_to_prompt_openai(scene: SceneContent):
    settings = load_api_settings()
    preset = load_preset()
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert at updating scene descriptions to create images using the Stable Diffusion model.\n"
                    "\n"
                    "Your job is to maintain and update character appearances and environmental descriptions based on ongoing dialogue.\n"
                    "\n"
                    "RULES:\n"
                    "1. Keep basic attributes (e.g., hair color, eye color) consistent unless explicitly changed in the scene.\n"
                    "2. Update dynamic elements (facial expressions, poses, clothing details) based on the current scene.\n"
                    "3. Maintain the continuity of the environment while updating with new details in the scene.\n"
                    "4. Use specific, clear, visually oriented English terminology.\n"
                    "5. Format output as comma-separated short phrases of no more than three words, e.g. long black hair, blue eyes, long legs, etc.\n"
                    "6. Choose appropriate camera angle for the image (e.g., wide shot, full body shot, close-up).\n"
                    "7. Select the appropriate image format from either landscape or portrait.\n"
                    "\n"
                    "Required format of the output (do not attach anything else):\n"
                    "Character Appearance: [physical characteristics, facial expression, clothing, pose],\n"
                    "Environment: [location details, lighting, atmosphere, objects],\n"
                    "[angle, shot],\n"
                    "Format: landscape/portrait"
                ),
            },
            {
                "role": "user",
                "content": (
                    "The current appearance and environment:\n"
                    f"{scene.prev_image_prompt}\n"
                    "\n"
                    "Update the character's appearance and environment above based on the following scene description:\n"
                    f"{scene.content}"
                ),
            },
        ]

        print("here")
        payload = make_openai_payload(messages, settings, preset, stream=True)
        print("payload:", payload)

        return await stream_post(
            f'{settings["custom_url"]}/chat/completions', settings["api_key"], payload, 0)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/scene-to-prompt")
async def scene_to_prompt(scene: SceneContent):
    settings = load_settings()
    if settings["api_type"] == "infermaticai":
        return await scene_to_prompt_infermaticai(scene)
    elif settings["api_type"] == "openai":
        return await scene_to_prompt_openai(scene)
    print("unknow api type: ", settings["api_type"])
    return ImagePrompt(prompt="")
