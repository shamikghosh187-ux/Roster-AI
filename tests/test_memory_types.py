from roster.memory_types import MemoryKind

def test_memory_kinds_are_stable():
    assert MemoryKind.PREFERENCE.value=="preference"
    assert set(item.value for item in MemoryKind) == {"fact","preference","goal","profile","context","task"}
