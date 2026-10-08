"""Convert ranked memories into bounded model context."""
from roster.memory_budget import within_budget

def to_context(ranked,max_items=8,max_chars=3000):
    records=[item[1] for item in ranked]
    return tuple({"key":r.key,"value":r.value,"kind":r.kind} for r in within_budget(records,max_items,max_chars))
