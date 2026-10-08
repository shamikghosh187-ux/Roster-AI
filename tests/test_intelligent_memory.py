from pathlib import Path

from roster.intelligent_memory import IntelligentMemory
from roster.storage import SQLiteMemoryStore


def make_memory(tmp_path: Path):
    store = SQLiteMemoryStore(tmp_path / "memory.db")
    return store, IntelligentMemory(store)


def test_explicit_memory_survives_new_instance(tmp_path):
    store, memory = make_memory(tmp_path)
    assert memory.learn_from_user("My name is Roster Tester") == 1

    reopened = SQLiteMemoryStore(tmp_path / "memory.db")
    recalled = IntelligentMemory(reopened).recall("what is my name?")
    assert any("Roster Tester" in item.content for item in recalled)


def test_relevant_recall_is_ranked(tmp_path):
    store, memory = make_memory(tmp_path)
    memory.remember("prefers concise answers", category="preference", importance=0.8)
    memory.remember("likes astrophysics", category="preference", importance=0.7)
    memory.remember("uses Windows", category="fact", importance=0.5)

    recalled = memory.recall("astrophysics")
    assert recalled
    assert recalled[0].content == "likes astrophysics"


def test_secret_like_content_is_not_persisted(tmp_path):
    store, memory = make_memory(tmp_path)
    assert not memory.remember("api_key=sk-abcdefghijklmnopqrstuvwxyz")
    assert store.all_memories() == []


def test_normal_chat_is_not_promoted_automatically(tmp_path):
    store, memory = make_memory(tmp_path)
    assert memory.learn_from_user("hello there, how are you?") == 0
    assert store.all_memories() == []


def test_explicit_remember_updates_existing_key(tmp_path):
    store, memory = make_memory(tmp_path)
    memory.remember("prefers short answers", category="preference", key="preference:response_style")
    memory.remember("prefers concise answers", category="preference", key="preference:response_style")
    rows = store.all_memories()
    assert len(rows) == 1
    assert rows[0][3] == "prefers concise answers"
