from roster.memory import ConversationMemory
from roster.storage import SQLiteMemoryStore


def test_sqlite_memory_persists(tmp_path):
    db = tmp_path / "memory.sqlite3"

    first = ConversationMemory(store=SQLiteMemoryStore(db))
    first.add("user", "remember this")
    first.add("assistant", "I will")

    second = ConversationMemory(store=SQLiteMemoryStore(db))
    messages = second.as_messages()

    assert messages == [
        {"role": "user", "content": "remember this"},
        {"role": "assistant", "content": "I will"},
    ]


def test_sqlite_memory_clear(tmp_path):
    db = tmp_path / "memory.sqlite3"

    memory = ConversationMemory(store=SQLiteMemoryStore(db))
    memory.add("user", "temporary")
    memory.clear()

    reopened = ConversationMemory(store=SQLiteMemoryStore(db))
    assert reopened.as_messages() == []
