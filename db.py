import os, sqlite3
from datetime import datetime
from typing import Optional, Tuple, List, Dict

DB_DIR = "data"
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

def insert_memory(user_id: int, title: str, desc: str, emotion: str,unlock_at_iso: Optional[str], media_path: Optional[str],media_type: Optional[str]) -> int:
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO memories(user_id,title,description,emotion,unlock_at,created_at,media_path,media_type)
            VALUES(?,?,?,?,?,?,?,?)
        """, (user_id, title, desc, emotion, unlock_at_iso, datetime.utcnow().isoformat(), media_path, media_type))
        conn.commit()
        return cur.lastrowid

def list_memories(user_id: int) -> List[Dict]:
    with get_conn() as conn:
        cur = conn.execute("""
            SELECT id,title,description,emotion,unlock_at,created_at,media_path,media_type
            FROM memories WHERE user_id=? ORDER BY created_at DESC
        """, (user_id,))
        rows = cur.fetchall()
    data = []
    for r in rows:
        data.append({
            "id": r[0], "title": r[1], "description": r[2], "emotion": r[3],
            "unlock_at": r[4], "created_at": r[5], "media_path": r[6], "media_type": r[7]
        })
    return data

