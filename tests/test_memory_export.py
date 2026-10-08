from roster.memory_export import export_records
from roster.memory_record import MemoryRecord

def test_export_contains_one_json_record_per_line():
    payload=export_records([MemoryRecord("a","1"),MemoryRecord("b","2")]); assert len(payload.strip().splitlines())==2
