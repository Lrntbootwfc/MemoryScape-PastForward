# storage.py

import os
import uuid
from typing import Tuple, IO
from PIL import Image
from io import BytesIO
from typing import AsyncGenerator
from fastapi import UploadFile
import aiofiles

def ensure_user_dir(user_id: int):
    media_root = os.getenv("MEDIA_ROOT", "uploads")
    user_dir = os.path.join(media_root, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def infer_media_type(filename: str) -> str:
    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return "image"
    if filename.lower().endswith(('.mp4', '.mov', '.avi')):
        return "video"
    return "other"

async def save_upload(user_id: int, file: UploadFile) -> Tuple[str, str]:
    user_dir = ensure_user_dir(user_id)
    uid = str(uuid.uuid4())
    safe_name = f"{uid}_{file.filename.replace(' ','_')}"
    disk_path = os.path.join(user_dir, safe_name)
    
    await file.seek(0)  
    # NEW: We will stream the file content to disk.
    async with aiofiles.open(disk_path, "wb") as f:
        while True:
            chunk = await file.read(1024)  # Read 1KB chunks
            if not chunk:
                break
            await f.write(chunk)
            
    media_type = infer_media_type(file.filename)
    
    if media_type == "image":
        try:
         with Image.open(disk_path)as img:
            img.load()
        except Exception:
            os.remove(disk_path)
            raise ValueError("Invalid image file.")
            
    relative_path = os.path.join(f"user_{user_id}", safe_name)
    return relative_path, media_type