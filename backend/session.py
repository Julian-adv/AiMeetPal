from fastapi import APIRouter
from pydantic import BaseModel
from settings import get_data_path
import os
import json
from datetime import datetime

router = APIRouter()

class Character(BaseModel):
    file_name: str
    image: str
    info: dict

class StoryEntry(BaseModel):
    id: int
    speaker: str
    content: str
    state: str
    image: str | None
    width: int | None
    height: int | None
    image_prompt: str | None

class Session(BaseModel):
    session_name: str
    selected_char: Character
    story_entries: list[dict]

@router.post("/api/save-session")
async def save_session(session: Session):
    try:
        if session.selected_char.file_name.endswith('.card'):
            file_name = session.selected_char.file_name[:-4]
        session_dir = get_data_path(f'sessions/{file_name}')
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        path = get_data_path(f'{session_dir}/{session.session_name}.json')
        with open(path, 'w') as f:
            json.dump(session.model_dump(), f, indent=2)
        return {"success": True}
    except Exception as e:
        print(f"Error creating sessions directory: {e}")
        return {"success": False}