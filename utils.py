from datetime import datetime, timezone
from typing import Optional, Dict, List


def iso_or_none(dt) -> Optional[str]:
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    return dt.astimezone(timezone.utc).isoformat()

def is_locked(unlock_iso: Optional[str]) -> bool:
    if not unlock_iso:
        return False
    try:
        unlock = datetime.fromisoformat(unlock_iso.replace("Z","+00:00"))
    except Exception:
        return False
    now = datetime.now(timezone.utc)
    return unlock > now

def get_memory_state(m: Dict) -> str:
    """Return bud, bloom, or fruit based on unlock status and age."""
    if is_locked(m.get("unlock_at")):
        return "bud"

    created_str = m.get("created_at")
    if not created_str or not isinstance(created_str, str) or created_str.strip() == "":
        return "bloom"

    try:
        created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
    except Exception:
        # fallback for invalid date formats
        return "bloom"

    try:
        age_days = (datetime.now(timezone.utc) - created_at).days
    except Exception:
        return "bloom"

    if age_days > 30:
        return "fruit"
    elif age_days > 7:
        return "bloom"
    else:
        return "bud"


def get_plant_size(memory: Dict) -> int:
    """Older memories are bigger."""
    created = datetime.fromisoformat(memory["created_at"].replace("Z","+00:00"))
    age_days = (datetime.now(timezone.utc) - created).days
    base = 50
    growth_rate = 0.3
    return min(int(base + growth_rate * age_days), 150)  # cap size

def group_memories_by_emotion(memories: List[Dict]) -> Dict[str, List[Dict]]:
    """Group memories so same emotion appear together."""
    groups = {}
    for m in memories:
        emo = m.get("emotion", "unknown")
        groups.setdefault(emo, []).append(m)
    return groups

