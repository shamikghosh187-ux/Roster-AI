"""Reject obviously unsafe memory payloads before persistence."""
import re
_SECRET=re.compile(r"(?:sk-|ghp_|xoxb-|AIza)[A-Za-z0-9_-]{12,}")

def sanitize(value: str) -> str:
    if _SECRET.search(value): raise ValueError("secret-like content cannot be persisted as memory")
    return value.strip()
