from roster.memory_record import MemoryRecord
from roster.memory_store import MemoryStore

def test_store_upserts_and_deletes_records():
    store=MemoryStore(); record=MemoryRecord("language","Python")
    store.upsert(record)
    assert store.get("language")==record
    assert store.delete("language")==record
    assert store.all()==()
