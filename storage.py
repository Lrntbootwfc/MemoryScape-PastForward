import os, uuid
from typing import Tuple, Optional
from PIL import Image
import streamlit as st

STORAGE_DIR = "storage"

def ensure_user_dir(user_id: int) -> str:
    path = os.path.join(STORAGE_DIR, str(user_id))
    os.makedirs(path, exist_ok=True)
    return path

def infer_media_type(filename: str, mime: Optional[str]) -> str:
    if mime:
        if mime.startswith("image/"): return "image"
        if mime.startswith("audio/"): return "audio"
        if mime.startswith("video/"): return "video"
    # fallback by extension
    ext = (filename or "").lower()
    if ext.endswith((".png",".jpg",".jpeg",".gif",".webp",".bmp")): return "image"
    if ext.endswith((".mp3",".wav",".m4a",".ogg",".flac")): return "audio"
    if ext.endswith((".mp4",".mov",".mkv",".webm")): return "video"
    if ext.endswith((".txt",".md",".pdf",".doc",".docx")): return "text"
    return "other"

def save_upload(user_id: int, file) -> Tuple[str, str]:
    """Returns (disk_path, media_type)"""
    user_dir = ensure_user_dir(user_id)
    uid = str(uuid.uuid4())
    safe_name = f"{uid}_{file.name.replace(' ','_')}"
    disk_path = os.path.join(user_dir, safe_name)
    with open(disk_path, "wb") as f:
        f.write(file.getbuffer())
    media_type = infer_media_type(file.name, file.type if hasattr(file, "type") else None)
    # Tiny optimization: ensure images are valid
    if media_type == "image":
        try:
            Image.open(disk_path).verify()
        except Exception:
            os.remove(disk_path)
            raise ValueError("Invalid image file.")
    return disk_path, media_type

