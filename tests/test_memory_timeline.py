from roster.memory_record import MemoryRecord
from roster.memory_timeline import timeline

def test_timeline_orders_by_creation_timestamp():
    a=MemoryRecord("a","1",created_at="2026-01-01T00:00:00+00:00"); b=MemoryRecord("b","2",created_at="2026-02-01T00:00:00+00:00"); assert [x.key for x in timeline([b,a])]==["a","b"]
