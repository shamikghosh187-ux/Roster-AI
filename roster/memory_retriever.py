"""High-level memory retrieval facade."""
from roster.memory_query import MemoryQuery

def retrieve(gateway,text,limit=5): return gateway.recall(MemoryQuery(text=text,limit=limit))
