from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import win32api

router = APIRouter()

class CurrentDirectory(BaseModel):
    path: str

class Entry(BaseModel):
    name: str
    is_dir: bool

class Entries(BaseModel):
    entries: List[Entry]
    current_directory: str

@router.post("/api/files")
async def get_files(cur_dir: CurrentDirectory):
    print(f"Current directory: {cur_dir.path}")
        
    # Get list of files and directories
    try:
        if cur_dir.path == "/":
            # Return list of drives for root
            drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]
            entries = [Entry(name=drive.rstrip('\\'), is_dir=True) for drive in drives]
            return Entries(
                entries=entries,
                current_directory="/"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
            
    # Get absolute path
    path = os.path.abspath(cur_dir.path)
    
    # Check if directory exists
    if not os.path.exists(path) or not os.path.isdir(path):
        raise HTTPException(status_code=404, detail="Directory not found")

    try:
        entries = os.listdir(path)
        entries = [Entry(name=entry, is_dir=os.path.isdir(os.path.join(path, entry))) for entry in entries]
        return Entries(
            entries=entries,
            current_directory=path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))