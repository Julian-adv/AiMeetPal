from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
import httpx
from settings import load_settings, load_preset
from payload import make_payload

router = APIRouter()

class SceneContent(BaseModel):
    content: str
    prev_image_prompt: str

class ImagePrompt(BaseModel):
    prompt: str

@router.post("/api/scene-to-prompt")
def scene_to_prompt(scene: SceneContent):
    settings = load_settings()
    preset = load_preset()
    try:
        system_prompt = (
            '<|im_start|>system\n' +
            'You are an expert at updating scene descriptions for Stable Diffusion image generation.\n' +
            '\n' +
            'Your task is to maintain and update character appearance and environment descriptions based on the ongoing conversation.\n' +
            '\n' +
            'RULES:\n' +
            '1. Keep consistent base attributes (like hair color, eye color) unless explicitly changed in the scene\n' +
            '2. Update dynamic elements (expressions, poses, clothing details) based on the current scene\n' +
            '3. Maintain environment continuity while updating with new details from the scene\n' +
            '4. Use specific, vivid, and Stable Diffusion-friendly English terms\n' +
            '5. Format output as comma-separated words or short phrases\n' +
            '\n' +
            'REQUIRED OUTPUT FORMAT:\n' +
            'character appearance: [physical attributes, current state, clothing]\n' +
            'environment: [location details, lighting, atmosphere, objects]\n' +
            '<|im_end|>\n' +
            '<|im_start|>user\n' +
            'Update character appearance and environment based on this scene description:\n' +
            scene.prev_image_prompt + '\n\n' +
            'scene description:\n' +
            scene.content +
            '<|im_end|>\n' +
            '<|im_start|>assistant\n' +
            '\n'
        )

        payload = make_payload(system_prompt, settings, preset, stream=False)

        with httpx.Client(timeout=httpx.Timeout(60.0, connect=30.0)) as client:
            print("generating image prompt...")
            print(payload)
            response = client.post(
                "https://api.totalgpt.ai/v1/completions",
                headers={
                    "Authorization": f"Bearer {settings['infermaticAiApiKey']}",
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
