from roster.memory_repository import MemoryRepository
from roster.agent_memory_bridge import remember_explicit

def test_bridge_persists_only_explicit_preferences():
    repo=MemoryRepository(); assert remember_explicit(repo,"I prefer Python."); assert repo.get("explicit_preference").value=="Python"
