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

class SaveSessionImage(BaseModel):
    character_name: str
    session_name: str
    index: str
    image: str  # base64 encoded image

class LoadSessionImage(BaseModel):
    character_name: str
    session_name: str
    index: int

@router.post("/api/save-session")
async def save_session(session: Session):
    try:
        if session.selected_char.file_name.endswith('.card'):
            file_name = session.selected_char.file_name[:-4]
        
        # Create directory for character and session
        session_dir = get_data_path(f'sessions/{file_name}/{session.session_name}')
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        # Save session data
        path = os.path.join(session_dir, 'session.json')
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
        char_dir = get_data_path(f'sessions/{data.name}')
        if not os.path.exists(char_dir):
            return {"success": False, "message": "No sessions found for this character"}

        # List all session directories and sort by modification time
        session_dirs = []
        for session_name in os.listdir(char_dir):
            session_path = os.path.join(char_dir, session_name)
            if os.path.isdir(session_path):
                json_path = os.path.join(session_path, 'session.json')
                if os.path.exists(json_path):
                    session_dirs.append((session_path, os.path.getmtime(json_path)))
        
        if not session_dirs:
            return {"success": False, "message": "No sessions found for this character"}

        # Get the most recent session directory
        latest_session_dir = max(session_dirs, key=lambda x: x[1])[0]
        session_name = os.path.basename(latest_session_dir)
        
        # Load and return the session data
        json_path = os.path.join(latest_session_dir, 'session.json')
        with open(json_path, 'r') as f:
            session_data = json.load(f)
            return {"success": True, "session": session_data, "session_name": session_name}

    except Exception as e:
        print(f"Error loading last session: {e}")
        return {"success": False, "message": str(e)}

@router.post("/api/save-session-image")
async def save_session_image(data: SaveSessionImage):
    try:
        # Create session directory path
        session_dir = get_data_path(f'sessions/{data.character_name}/{data.session_name}')
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        # Save image
        image_name = f"{data.index}.png"
        image_path = os.path.join(session_dir, image_name)
        
        # Decode base64 and save image
        import base64
        image_data = base64.b64decode(data.image.split(',')[1] if ',' in data.image else data.image)
        with open(image_path, 'wb') as f:
            f.write(image_data)
            
        # Return relative path from data directory
        relative_path = f'sessions/{data.character_name}/{data.session_name}/{image_name}'
        return {"success": True, "path": relative_path}

    except Exception as e:
        print(f"Error saving session image: {e}")
        return {"success": False, "message": str(e)}

@router.post("/api/load-session-image")
async def load_session_image(data: LoadSessionImage):
    try:
        # Create image path
        session_dir = get_data_path(f'sessions/{data.character_name}/{data.session_name}')
        image_path = os.path.join(session_dir, f"{data.index}.png")
        
        if not os.path.exists(image_path):
            return {"success": False, "message": "Image not found"}
            
        # Read and encode image
        import base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            return {"success": True, "image": f"data:image/png;base64,{base64_image}"}

    except Exception as e:
        print(f"Error loading session image: {e}")
        return {"success": False, "message": str(e)}