# backend/server.py
import os
from datetime import datetime
from typing import List, Optional,Tuple
from io import BytesIO
import random 
from concurrent.futures import ThreadPoolExecutor 
import asyncio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request ,Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
from fastapi.routing import APIRouter

from auth import ensure_db, login, signup
from db import list_memories, insert_memory,delete_memories
from storage import save_upload_sync
from emotions import classify


# ---------- Config ----------
API_TITLE = "MemoryScape API"
API_VERSION = "0.1.0"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "uploads")   # where storage.save_upload puts files

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

ensure_db()

if os.path.isdir(MEDIA_ROOT):
    app.mount("/media", StaticFiles(directory=MEDIA_ROOT), name="media")

react_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Memory_Garden', 'dist'))
if os.path.isdir(react_dist_path):
    app.mount("/", StaticFiles(directory=react_dist_path, html=True), name="react_app")

# ---------- Schemas ----------
class UserOut(BaseModel):
    id: int
    name: str
    email: str

class MemoryOut(BaseModel):
    id: int
    user_id: int
    title: str
    description:str
    emotion: Optional[str] = None
    unlock_at_iso: Optional[str] = None
    created_at: Optional[str] =None
    media_path: Optional[str] = None
    media_type: Optional[str] = None
    position: Optional[List[float]] = None
    memory: Optional[dict] = None 

class SearchQuery(BaseModel):
    user_id: int
    q: Optional[str] = None
    emotion: Optional[str] = None
    date_from: Optional[str] = None  # ISO date or yyyy-mm-dd
    date_to: Optional[str] = None
    
class DeleteRequest(BaseModel):
    user_id: int
    memory_ids: List[int]


# ---------- Helpers ----------
def normalize_date(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        try:
            return datetime.strptime(s, "%Y-%m-%d")
        except Exception:
            return None
        
def get_media_url(request: Request, relative_path: str) -> str:
    if not relative_path:
        return None
    base = str(request.base_url).rstrip("/")
    norm = str(relative_path).replace("\\", "/")
    return f"{base}/media/{norm}"

def to_out(row,request: Request) -> MemoryOut:
    media_path = row.get("media_path")
    media_type = row.get("media_type")
    
    memory_info = None
    if media_path and media_type:
        full_url = get_media_url(request, media_path)
        memory_info = {"source": full_url, "type": media_type}
    
    
    row['memory'] = memory_info
    out = MemoryOut(**row)
    if out.media_path:
        out.media_path = get_media_url(request, out.media_path)
    return out

def generate_random_position() -> Tuple[float, float, float]:
    return [random.uniform(-20, 20), 0, random.uniform(-20, 20)]

# ---------- Routes ----------
@api_router.get("/health")
def health():
    return {"ok": True, "service": API_TITLE, "version": API_VERSION}

@api_router.post("/login", response_model=UserOut)
def api_login(email: str = Form(...), password: str = Form(...)):
    user = login(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

@api_router.post("/signup", response_model=UserOut)
def api_signup(email: str = Form(...), name: str = Form(...), password: str = Form(...)):
    print("Received signup:", email, name, password)
    created = signup(email, name, password)
    if not created:
        raise HTTPException(status_code=400, detail="Signup failed")
    user = login(email, password)
    return user

# @app.get("/memorygarden", response_class=PlainTextResponse)
# def memorygarden_landing():
#     return "Memory Garden endpoint is reachable. Use the Streamlit app or the React UI."

@api_router.get("/memories", response_model=List[MemoryOut])
def api_list_memories(user_id: int, request: Request):
    rows = list_memories(user_id)
    if not rows:
        return []
    
    for r in rows:
        r['position'] = generate_random_position()
    return [to_out(r, request) for r in rows]

@api_router.get("/memories/search", response_model=List[MemoryOut])
def api_search_memories(
    request: Request,
    user_id: int,
    q: Optional[str] = None,
    emotion: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    
):
    rows = list_memories(user_id)
    if not rows:
        return []
    for r in rows:
        r['position'] = generate_random_position()

    if q:
        ql = q.lower()
        rows = [r for r in rows if ql in (f"{r.get('title','')}{r.get('description','')}").lower()]
    if emotion:
        rows = [r for r in rows if (r.get("emotion") or "").lower() == emotion.lower()]
    d_from = normalize_date(date_from)
    d_to = normalize_date(date_to)
    if d_from or d_to:
        tmp = []
        for r in rows:
            unlock_iso = r.get("unlock_at")
            try:
                d = datetime.fromisoformat(unlock_iso) if unlock_iso else None
            except Exception:
                d = None
            ok = True
            if d_from and d and d < d_from:
                ok = False
            if d_to and d and d > d_to:
                ok = False
            if ok:
                tmp.append(r)
        rows = tmp
    return [to_out(r,request) for r in rows]

@api_router.post("/memories", response_model=MemoryOut)
async def api_create_memory(
    request: Request,
    user_id: int = Form(...),
    title: str = Form(...),
    desc: str = Form(""),
    unlock_at_iso: Optional[str] = Form(None),
    emotion: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    
):
    if not emotion:
        label, _plant = classify(f"{title}\n{desc or ''}")
        emotion = label

    media_path, media_type = (None, None)
    if file is not None:

        try:
            content = await file.read()
            media_path, media_type = await asyncio.get_event_loop().run_in_executor(
                executor, save_upload_sync, user_id, content, file.filename
            # media_path, media_type = await save_upload(user_id,file)
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Upload failed: {e}")

    mem_id = insert_memory(
        user_id=user_id,
        title=title,
        desc=desc or "",
        emotion=emotion,
        unlock_at_iso=unlock_at_iso,
        media_path=media_path,
        media_type=media_type,
    )
    rows = list_memories(user_id)
    created = next((r for r in rows if r["id"] == mem_id), None)
    if not created:
        raise HTTPException(status_code=500, detail="Created but not found")
    return to_out(created, request)

@api_router.delete("/memories", status_code=204)
def api_delete_memories(request_data: DeleteRequest = Body(...)):
    success = delete_memories(request_data.user_id, request_data.memory_ids)
    if not success:
        raise HTTPException(status_code=400, detail="Could not delete all memories")
    return
    
app.include_router(api_router)