"""Atomic-in-intent batch operations for memory repositories."""
from roster.memory_record import MemoryRecord

class MemoryBatch:
    def __init__(self,repository): self.repository=repository; self._records=[]
    def add(self,record:MemoryRecord): self._records.append(record); return self
    def commit(self):
        accepted=[]
        for record in self._records:
            if self.repository.save(record): accepted.append(record)
        self._records.clear(); return tuple(accepted)
