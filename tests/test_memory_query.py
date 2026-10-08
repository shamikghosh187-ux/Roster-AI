from roster.memory_query import MemoryQuery

def test_memory_query_defaults_are_safe():
    query=MemoryQuery(text="python"); assert query.limit==10 and query.minimum_score==0

def test_memory_query_rejects_invalid_limits():
    try: MemoryQuery(limit=0)
    except ValueError: pass
    else: raise AssertionError("expected validation error")
