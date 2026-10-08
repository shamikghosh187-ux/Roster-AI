from roster.memory_conflict import detect_conflict
from roster.memory_record import MemoryRecord

def test_conflicting_values_are_detected():
    old=MemoryRecord("city","Asansol"); new=MemoryRecord("city","Kolkata")
    conflict=detect_conflict(old,new)
    assert conflict and conflict.key=="city"

def test_same_value_is_not_a_conflict():
    record=MemoryRecord("city","Asansol"); assert detect_conflict(record,record) is None
