"""Conflict detection between candidate memories sharing a key."""
from dataclasses import dataclass
from roster.memory_record import MemoryRecord

@dataclass(frozen=True)
class MemoryConflict:
    key: str
    existing: MemoryRecord
    candidate: MemoryRecord

def detect_conflict(existing: MemoryRecord|None,candidate: MemoryRecord) -> MemoryConflict|None:
    if existing is None or existing.value == candidate.value: return None
    return MemoryConflict(candidate.key,existing,candidate)
