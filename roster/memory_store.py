"""Thread-safe in-process store for structured memories."""
from threading import RLock
from roster.memory_record import MemoryRecord

class MemoryStore:
    def __init__(self):
        self._records:dict[str,MemoryRecord]={}
        self._lock=RLock()
    def upsert(self,record:MemoryRecord)->MemoryRecord:
        if not isinstance(record,MemoryRecord): raise TypeError("record must be a MemoryRecord")
        with self._lock:
            self._records[record.key]=record
            return record
    def get(self,key):
        with self._lock:return self._records.get(key)
    def delete(self,key):
        with self._lock:return self._records.pop(key,None)
    def all(self):
        with self._lock:return tuple(self._records.values())
    def clear(self):
        with self._lock:self._records.clear()
    def __len__(self):
        with self._lock:return len(self._records)
