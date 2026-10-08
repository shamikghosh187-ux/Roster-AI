"""Protocol-like in-process store for structured memories."""
from roster.memory_record import MemoryRecord

class MemoryStore:
    def __init__(self): self._records: dict[str,MemoryRecord]={}
    def upsert(self, record: MemoryRecord) -> MemoryRecord:
        self._records[record.key]=record
        return record
    def get(self,key): return self._records.get(key)
    def delete(self,key): return self._records.pop(key,None)
    def all(self): return tuple(self._records.values())
    def clear(self): self._records.clear()
