from roster.memory_record import MemoryRecord
from roster.memory_serializer import dumps,loads

def test_memory_round_trip_is_lossless():
    record=MemoryRecord("x","y",metadata={"source_id":"1"}); assert loads(dumps(record))==record
