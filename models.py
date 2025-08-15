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

