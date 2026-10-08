from roster.memory_conflict import detect_conflict
from roster.memory_record import MemoryRecord
from roster.memory_resolver import resolve

def test_resolver_prefers_higher_confidence():
    old=MemoryRecord("x","old",confidence=.5); new=MemoryRecord("x","new",confidence=.9)
    assert resolve(detect_conflict(old,new)).value=="new"
