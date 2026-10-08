from roster.memory_context_adapter import to_context
from roster.memory_record import MemoryRecord

def test_context_adapter_emits_safe_structured_fields():
    result=to_context([(1,MemoryRecord("x","y"))]); assert result==({"key":"x","value":"y","kind":"fact"},)
