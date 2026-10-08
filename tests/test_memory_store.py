from roster.memory_record import MemoryRecord
from roster.memory_store import MemoryStore

def test_store_upserts_and_deletes_records():
    store=MemoryStore(); record=MemoryRecord("language","Python")
    store.upsert(record)
    assert store.get("language")==record
    assert store.delete("language")==record
    assert store.all()==()


def test_store_rejects_non_memory_records():
    import pytest
    with pytest.raises(TypeError): MemoryStore().upsert(object())

def test_store_reports_size():
    store=MemoryStore()
    store.upsert(MemoryRecord("language","Python"))
    assert len(store)==1
