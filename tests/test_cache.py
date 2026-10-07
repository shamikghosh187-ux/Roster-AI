from roster.cache import TTLCache
def test_cache_round_trip_and_clear():
    c=TTLCache(); c.set("answer",42); assert c.get("answer")==42; c.clear(); assert c.get("answer") is None
def test_cache_eviction():
    c=TTLCache(1); c.set("a",1); c.set("b",2); assert c.get("a") is None; assert c.get("b")==2
