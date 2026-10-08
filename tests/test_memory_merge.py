from roster.memory_merge import merge
from roster.memory_record import MemoryRecord

def test_merge_deduplicates_equal_records():
    old=MemoryRecord("x","same"); new=MemoryRecord("x","same"); assert merge(old,new) is old
