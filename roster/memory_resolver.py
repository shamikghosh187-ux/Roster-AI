"""Conflict resolution rules for durable memory candidates."""
from roster.memory_record import MemoryRecord
from roster.memory_conflict import MemoryConflict

def resolve(conflict: MemoryConflict) -> MemoryRecord:
    old,new=conflict.existing,conflict.candidate
    if new.confidence > old.confidence: return new
    if new.confidence < old.confidence: return old
    if new.importance >= old.importance: return new
    return old
