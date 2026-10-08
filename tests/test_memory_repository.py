from roster.memory_policy import MemoryPolicy
from roster.memory_record import MemoryRecord
from roster.memory_repository import MemoryRepository

def test_repository_rejects_records_outside_policy():
    repo=MemoryRepository(policy=MemoryPolicy(minimum_confidence=.8))
    assert repo.save(MemoryRecord("x","y",confidence=.5)) is False
    assert repo.all()==()

def test_repository_accepts_allowed_records():
    repo=MemoryRepository(); assert repo.save(MemoryRecord("x","y")); assert repo.get("x").value=="y"
