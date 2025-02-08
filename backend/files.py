from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import win32api
from send2trash import send2trash

router = APIRouter()


class CurrentDirectory(BaseModel):
    path: str


class Entry(BaseModel):
    name: str
    is_dir: bool


class Entries(BaseModel):
    entries: List[Entry]
    current_directory: str


class SaveJson(BaseModel):
    path: str
    json_data: dict


class SaveImage(BaseModel):
    path: str
    image: str  # base64 encoded image data


@router.post("/api/files")
async def get_files(cur_dir: CurrentDirectory):
    print(f"Current directory: {cur_dir.path}")

    # Get list of files and directories
    try:
        if cur_dir.path == "/":
            # Return list of drives for root
            drives = win32api.GetLogicalDriveStrings().split("\000")[:-1]
            entries = [Entry(name=drive.rstrip("\\"), is_dir=True) for drive in drives]
            return Entries(entries=entries, current_directory="/")
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
        entries.sort(key=lambda x: (not x.is_dir, x.name.lower()))
        return Entries(entries=entries, current_directory=path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/save-json")
async def save_json(data: SaveJson):
    # Ensure the path is under /data directory
    base_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
    full_path = os.path.normpath(os.path.join(base_path, data.path.lstrip("/")))

    # Security check - ensure the path is under /data directory
    if not os.path.commonpath([base_path]) == os.path.commonpath([base_path, full_path]):
        raise HTTPException(status_code=400, detail="Invalid path - must be under /data directory")

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Save JSON data
        import json

        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data.json_data, f, ensure_ascii=False, indent=2)

        print(f"save json: {data.path}")
        return {"status": "success", "path": data.path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/save-image")
async def save_image(data: SaveImage):
    # Ensure the path is under /data directory
    base_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
    full_path = os.path.normpath(os.path.join(base_path, data.path.lstrip("/")))

    # Security check - ensure the path is under /data directory
    if not os.path.commonpath([base_path]) == os.path.commonpath([base_path, full_path]):
        raise HTTPException(status_code=400, detail="Invalid path - must be under /data directory")

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Decode base64 image and save
        import base64

        # Remove data URL prefix if present (e.g., "data:image/png;base64,")
        if "," in data.image:
            data.image = data.image.split(",", 1)[1]

        image_data = base64.b64decode(data.image)
        with open(full_path, "wb") as f:
            f.write(image_data)

        return {"status": "success", "path": data.path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SaveBinary(BaseModel):
    path: str
    binary: bytes


@router.post("/api/save-binary")
async def save_binary(data: SaveBinary):
    # Ensure the path is under /data directory
    base_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
    full_path = os.path.normpath(os.path.join(base_path, data.path.lstrip("/")))

    # Security check - ensure the path is under /data directory
    if not os.path.commonpath([base_path]) == os.path.commonpath([base_path, full_path]):
        raise HTTPException(status_code=400, detail="Invalid path - must be under /data directory")

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Save binary data
        with open(full_path, "wb") as f:
            f.write(data.binary)

        return {"status": "success", "path": data.path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DeleteFile(BaseModel):
    path: str


@router.post("/api/delete-file")
async def delete_file(data: DeleteFile):
    # Ensure the path is under /data directory
    base_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data"))
    full_path = os.path.normpath(os.path.join(base_path, data.path.lstrip("/")))

    # Security check - ensure the path is under /data directory
    if not os.path.commonpath([base_path]) == os.path.commonpath([base_path, full_path]):
        raise HTTPException(status_code=400, detail="Invalid path - must be under /data directory")

    try:
        # Move the file to recycle bin instead of deleting
        send2trash(full_path)

        return {"status": "success", "path": data.path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
