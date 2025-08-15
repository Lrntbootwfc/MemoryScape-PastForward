from datetime import datetime, timezone
from typing import Optional

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

