"""Repository boundary for memory persistence and policy enforcement."""
from roster.memory_policy import MemoryPolicy
from roster.memory_record import MemoryRecord
from roster.memory_store import MemoryStore

class MemoryRepository:
    def __init__(self,store=None,policy=None):
        self.store=store or MemoryStore(); self.policy=policy or MemoryPolicy()
    def save(self,record):
        if not self.policy.accepts(record.confidence,record.kind): return False
        self.store.upsert(record); return True
    def get(self,key): return self.store.get(key) if self.policy.enabled else None
    def all(self): return self.store.all() if self.policy.enabled else ()
