from roster.memory_record import MemoryRecord
from roster.sqlite_memory_repository import SQLiteMemoryRepository

def test_sqlite_repository_round_trips_structured_memory(tmp_path):
    repo=SQLiteMemoryRepository(tmp_path/"memory.db"); record=MemoryRecord("language","Python",metadata={"source":"chat"}); assert repo.save(record); assert repo.get("language")==record
