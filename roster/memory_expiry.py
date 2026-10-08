"""Retention calculations for memory records."""
from datetime import datetime, timedelta, timezone

def is_expired(created_at: str, retention_days: int, *, now: datetime|None=None) -> bool:
    if retention_days < 0: raise ValueError("retention_days cannot be negative")
    created=datetime.fromisoformat(created_at.replace("Z","+00:00"))
    current=now or datetime.now(timezone.utc)
    return current-created >= timedelta(days=retention_days)
