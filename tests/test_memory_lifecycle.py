from datetime import datetime,timezone,timedelta
from roster.memory_lifecycle import cleanup
from roster.memory_repository import MemoryRepository
from roster.memory_record import MemoryRecord

def test_cleanup_removes_expired_in_memory_records():
    repo=MemoryRepository(); now=datetime.now(timezone.utc); repo.save(MemoryRecord("old","x",created_at=(now-timedelta(days=10)).isoformat())); assert cleanup(repo,7,now=now)==("old",); assert repo.get("old") is None
