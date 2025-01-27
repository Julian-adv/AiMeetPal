from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
import httpx
from settings import load_api_settings, load_preset
from payload import make_payload

router = APIRouter()

class SceneContent(BaseModel):
    content: str
    prev_image_prompt: str

class ImagePrompt(BaseModel):
    prompt: str

@router.post("/api/scene-to-prompt")
def scene_to_prompt(scene: SceneContent):
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
            print("generating image prompt...")
            print(f"prev_image_prompt: {scene.prev_image_prompt}")
            print(f"content: {scene.content}")
            response = client.post(
                "https://api.totalgpt.ai/v1/completions",
                headers={
                    "Authorization": f"Bearer {settings['api_key']}",
                    "Content-Type": "application/json"
                },
                json=payload
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
