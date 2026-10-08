"""Duplicate detection for normalized memory keys and values."""
import re

def normalize_text(value: str) -> str:
    return re.sub(r"\\s+"," ",value.strip().lower())

def duplicate_key(key: str, value: str) -> str:
    return normalize_text(key)+"::"+normalize_text(value)
