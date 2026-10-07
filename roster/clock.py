"""Injectable clock helpers for deterministic runtime code and tests."""
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

def utc_timestamp() -> str:
    return utc_now().isoformat(timespec="milliseconds")

def unix_time() -> float:
    return utc_now().timestamp()
