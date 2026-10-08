from roster.memory_batch import MemoryBatch
from roster.memory_record import MemoryRecord
from roster.memory_repository import MemoryRepository

def test_batch_commits_accepted_records():
    repo=MemoryRepository(); batch=MemoryBatch(repo).add(MemoryRecord("a","1")).add(MemoryRecord("b","2")); assert len(batch.commit())==2
