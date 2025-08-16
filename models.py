from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Memory:
    id: int
    user_id: int
    title: str
    description: str
    emotion: str
    unlock_at: Optional[datetime]
    created_at: datetime
    media_path: Optional[str]
    media_type: Optional[str]  # 'image','audio','video','text','other'
    state: Optional[str] = None  # 'bud', 'bloom', 'fruit'
    size: Optional[int] = None   # size in pixels (or scaling factor)
    group_id: Optional[str] = None  # for related memories
