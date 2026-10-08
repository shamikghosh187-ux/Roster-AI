from pathlib import Path

from roster.intelligent_memory import IntelligentMemory
from roster.storage import SQLiteMemoryStore


def test_failure_learning_is_persisted_and_recalled(tmp_path: Path):
    memory = IntelligentMemory(SQLiteMemoryStore(tmp_path / "memory.db"))
    assert memory.record_failure(
        "open study notes",
        "FileNotFoundError: notes.txt",
        ["search", "list_files"],
    )

    recalled = memory.recall("study notes notes.txt")
    assert recalled
    assert recalled[0].category == "failure"
    assert "FileNotFoundError" in recalled[0].content


def test_failure_learning_rejects_secret_like_data(tmp_path: Path):
    memory = IntelligentMemory(SQLiteMemoryStore(tmp_path / "memory.db"))
    assert not memory.record_failure(
        "configure provider",
        "api_key=sk-abcdefghijklmnopqrstuvwxyz",
    )
    assert memory.store.all_memories() == []
