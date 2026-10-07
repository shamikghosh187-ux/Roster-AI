"""Shared text normalization helpers."""
import re
_WHITESPACE=re.compile(r"\s+")
def normalize_text(value:str)->str: return _WHITESPACE.sub(" ",(value or "").strip())
def truncate(value:str,limit:int)->str:
    if limit<1: raise ValueError("limit must be positive")
    text=normalize_text(value)
    return text if len(text)<=limit else text[:max(0,limit-1)]+"…"
