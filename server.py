# backend/server.py

import os
from datetime import datetime
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor 
import asyncio

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.routing import APIRouter

from db import list_memories, insert_memory, delete_memories
from storage import save_upload_sync
from emotions import classify

# ---------- Config ----------
API_TITLE = "MemoryScape API"
API_VERSION = "0.1.0"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "uploads")

# ---------- App ----------
app = FastAPI(title=API_TITLE, version=API_VERSION)
api_router = APIRouter(prefix="/api")
executor = ThreadPoolExecutor(max_workers=5)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount media folder for serving files
os.makedirs(MEDIA_ROOT, exist_ok=True)
app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")

def to_out(row: dict, request: Request) -> dict:
    if row.get("media_path"):
        # Use the full relative path from the database
        row["media_path"] = f"/media/{row['media_path']}"
        # row["media_path"] = str(request.base_url.replace(path=f"/media/{row['media_path']}"))
    return row



# ---------- API Models ----------
class MemoryResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    emotion: str
    unlock_at: Optional[str]
    created_at: str
    media_path: Optional[str]
    media_type: Optional[str]
    model_path: Optional[str]

class DeleteRequest(BaseModel):
    user_id: int
    memory_ids: List[int]

# ---------- API Routes ----------
@api_router.get("/memories", response_model=List[MemoryResponse])
def get_user_memories(user_id: int, request: Request):
    """Lists all memories for a given user."""
    rows = list_memories(user_id)
    return [to_out(r, request) for r in rows]

@api_router.post("/memories", status_code=201, response_model=MemoryResponse)
async def create_memory(
    request: Request,
    user_id: int = Form(...),
    title: str = Form(...),
    desc: Optional[str] = Form(""),
    unlock_at_iso: Optional[str] = Form(""),
    emotion: Optional[str] = Form(None),
    model_path: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """Creates a new memory, with optional media upload."""
    if not emotion:
        label, _ = classify(f"{title}\n{desc or ''}")
        emotion = label

    media_path, media_type = None, None
    if file:
        try:
            content = await file.read()
            # Run the synchronous file-saving operation in a thread pool
            media_path, media_type = await asyncio.get_event_loop().run_in_executor(
                executor, save_upload_sync, user_id, content, file.filename
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Upload failed: {e}")

    mem_id = insert_memory(
        user_id=user_id,
        title=title,
        desc=desc or "",
        emotion=emotion,
        unlock_at_iso=unlock_at_iso or None, # Ensure None is passed if string is empty
        media_path=media_path,
        media_type=media_type,
        model_path=model_path
    )
    
    rows = list_memories(user_id)
    created = next((r for r in rows if r["id"] == mem_id), None)
    if not created:
        raise HTTPException(status_code=500, detail="Memory created but could not be found.")
        
    return to_out(created, request)

@api_router.post("/memories/delete", status_code=204)
def delete_multiple_memories(request_data: DeleteRequest = Body(...)):
    """Deletes one or more memories for a specific user."""
    if not request_data.memory_ids:
        return

    try:
        # Pass user_id to the database function for secure deletion
        deleted = delete_memories(
            user_id=request_data.user_id, 
            memory_ids=request_data.memory_ids
        )
        if not deleted:
            print(f"Deletion attempt for user {request_data.user_id}, IDs {request_data.memory_ids} found nothing to delete.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not delete memories: {e}")
    
    return

app.include_router(api_router)