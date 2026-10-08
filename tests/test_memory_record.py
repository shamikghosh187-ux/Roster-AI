from roster.memory_record import MemoryRecord

def test_memory_record_validates_and_scores():
    record=MemoryRecord("name","Roster",confidence=.8,importance=.5)
    assert record.score == .4

def test_memory_record_rejects_invalid_confidence():
    try: MemoryRecord("x","y",confidence=2)
    except ValueError as exc: assert "confidence" in str(exc)
    else: raise AssertionError("expected validation error")
