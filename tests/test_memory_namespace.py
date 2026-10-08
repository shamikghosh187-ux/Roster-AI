from roster.memory_namespace import MemoryNamespace

def test_namespace_prevents_key_collisions():
    assert MemoryNamespace("session").key("city")=="session:city"
