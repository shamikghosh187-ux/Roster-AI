"""Stable JSON serialization for memory records."""
import json
from dataclasses import asdict
from roster.memory_record import MemoryRecord

def dumps(record: MemoryRecord) -> str:
    return json.dumps(asdict(record),ensure_ascii=False,sort_keys=True)

def loads(payload: str) -> MemoryRecord:
    data=json.loads(payload)
    if not isinstance(data,dict): raise ValueError("memory payload must be an object")
    return MemoryRecord(**data)
