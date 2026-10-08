"""Conservative extraction of explicit user preferences from text."""
import re
from roster.memory_record import MemoryRecord

def extract_explicit_preference(text: str):
    match=re.search(r"\\bI (?:prefer|like|love|want) ([^.!?]+)",text,re.I)
    if not match:return None
    value=match.group(1).strip()
    return MemoryRecord(key="explicit_preference",value=value,kind="preference",confidence=.8,importance=.6,source="explicit_text")
