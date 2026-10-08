"""Optional bridge from conversation text to explicit durable memory."""
from roster.memory_extractor import extract_explicit_preference
from roster.memory_sanitizer import sanitize
from roster.memory_record import MemoryRecord

def remember_explicit(repository,text):
    record=extract_explicit_preference(text)
    if record is None:return False
    safe=MemoryRecord(record.key,sanitize(record.value),record.kind,record.confidence,record.importance,record.source,record.created_at,record.metadata)
    return repository.save(safe)
