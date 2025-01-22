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

class LoadLastSession(BaseModel):
    name: str

@router.post("/api/load-last-session")
async def load_last_session(data: LoadLastSession):
    try:
        # Get the sessions directory for the character
        session_dir = get_data_path(f'sessions/{data.name}')
        if not os.path.exists(session_dir):
            return {"success": False, "message": "No sessions found for this character"}

        # List all session files and sort by modification time
        session_files = []
        for file in os.listdir(session_dir):
            if file.endswith('.json'):
                file_path = os.path.join(session_dir, file)
                session_files.append((file_path, os.path.getmtime(file_path)))
        
        if not session_files:
            return {"success": False, "message": "No sessions found for this character"}

        # Get the most recent session file
        latest_session = max(session_files, key=lambda x: x[1])[0]
        
        # Load and return the session data
        with open(latest_session, 'r') as f:
            session_data = json.load(f)
            session_name = os.path.splitext(os.path.basename(latest_session))[0]
            return {"success": True, "session": session_data, "session_name": session_name}

    except Exception as e:
        print(f"Error loading last session: {e}")
        return {"success": False, "message": str(e)}
