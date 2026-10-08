from roster.memory_export import export_records
from roster.memory_import import import_records
from roster.memory_record import MemoryRecord

def test_import_round_trips_exported_records():
    records=(MemoryRecord("a","1"),MemoryRecord("b","2")); assert import_records(export_records(records))==records
