# db.py

import os, sqlite3,tempfile
from datetime import datetime
from typing import Optional, Tuple, List, Dict

DB_DIR = os.path.join(tempfile.gettempdir(), "data")
DB_PATH = os.path.join(DB_DIR, "memoryscape.db")

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password_hash BLOB NOT NULL,
            created_at TEXT NOT NULL
        );
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            emotion TEXT NOT NULL,
            unlock_at TEXT,
            created_at TEXT NOT NULL,
            media_path TEXT,
            media_type TEXT,
            model_path TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
        conn.commit()

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def create_user(email: str, name: str, password_hash: bytes) -> Tuple[bool, Optional[str]]:
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO users(email,name,password_hash,created_at) VALUES(?,?,?,?)",
                (email, name, password_hash, datetime.utcnow().isoformat())
            )
            conn.commit()
        return True, None
    except sqlite3.IntegrityError as e:
        return False, "Email already registered"

def get_user_by_email(email: str) -> Optional[Tuple]:
    with get_conn() as conn:
        cur = conn.execute("SELECT id,email,name,password_hash,created_at FROM users WHERE email=?", (email,))
        return cur.fetchone()

def insert_memory(user_id: int, title: str, desc: str, emotion: str,unlock_at_iso: Optional[str], media_path: Optional[str],media_type: Optional[str],model_path: Optional[str]) -> int:
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO memories(user_id,title,description,emotion,unlock_at,created_at,media_path,media_type, model_path)
            VALUES(?,?,?,?,?,?,?,?,?)
            """, (user_id, title, desc, emotion, unlock_at_iso, datetime.utcnow().isoformat(), media_path, media_type, model_path))
        conn.commit()
        return cur.lastrowid

def list_memories(user_id: int) -> List[Dict]:
    with get_conn() as conn:
        cur = conn.execute("""
            SELECT id, user_id, title, description, emotion, unlock_at, created_at, media_path, media_type, model_path
            FROM memories WHERE user_id=? ORDER BY created_at DESC
        """, (user_id,))
        rows = cur.fetchall()
    
    data = []
    for r in rows:
        data.append({
            "id": r[0], "user_id": r[1], "title": r[2], "description": r[3], "emotion": r[4],
            "unlock_at": r[5], "created_at": r[6], "media_path": r[7], "media_type": r[8],
            "model_path": r[9] 
        })
    return data


def delete_memories(user_id: int, memory_ids: List[int]) -> bool:
    """
    Deletes memories from the database that match the provided IDs AND the user_id.
    Also removes their associated media files from storage.
    """
    if not memory_ids or not user_id:
        return False

    media_root = os.getenv("MEDIA_ROOT", "uploads")
    placeholders = ",".join("?" for _ in memory_ids)
    
    # Parameters for the SQL query, including the user_id for the WHERE clause
    params = memory_ids + [user_id]

    with get_conn() as conn:
        # First, find the media paths for the memories that belong to the user
        cursor = conn.execute(
            f"SELECT media_path FROM memories WHERE id IN ({placeholders}) AND user_id = ?",
            params
        )
        paths_to_delete = [row[0] for row in cursor.fetchall() if row[0]]

        # Now, execute the delete operation, ensuring it's for the correct user
        cursor = conn.execute(
            f"DELETE FROM memories WHERE id IN ({placeholders}) AND user_id = ?",
            params
        )
        conn.commit()

        # If rows were deleted, proceed to remove the associated files
        if cursor.rowcount > 0:
            for path in paths_to_delete:
                full_path = os.path.join(media_root, path)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except OSError as e:
                        print(f"Error deleting file {full_path}: {e}")
            return True
            
    return False