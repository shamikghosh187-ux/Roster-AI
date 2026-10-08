from pathlib import Path

from roster.intelligent_memory import IntelligentMemory
from roster.recovery_strategy import RecoveryStrategy, RecoveryStrategySelector
from roster.storage import SQLiteMemoryStore


def test_distinct_failures_do_not_overwrite_each_other(tmp_path: Path):
    memory = IntelligentMemory(SQLiteMemoryStore(tmp_path / "memory.db"))
    assert memory.record_failure("open notes", "missing notes.txt")
    assert memory.record_failure("open notes", "permission denied")
    failures = [m for m in memory.store.all_memories() if m[2] == "failure"]
    assert len(failures) == 2


def test_recovery_strategy_uses_verified_history(tmp_path: Path):
    store = SQLiteMemoryStore(tmp_path / "memory.db")
    store.record_recovery_experience("goal", "failure", "replan", True, "verified")
    store.record_recovery_experience("goal", "failure", "replan", True, "verified")
    store.record_recovery_experience("goal", "failure", "retry_once", False, "failed")
    selector = RecoveryStrategySelector(store)

    ranked = selector.rank("goal", "failure")
    assert ranked[0].strategy is RecoveryStrategy.REPLAN
    assert ranked[0].successes == 2
    assert ranked[0].failures == 0


def test_recovery_strategy_has_neutral_prior_without_history(tmp_path: Path):
    selector = RecoveryStrategySelector(SQLiteMemoryStore(tmp_path / "memory.db"))
    result = selector.score("new goal", "new failure", RecoveryStrategy.INSPECT_STATE)
    assert result.samples == 0
    assert result.score == 0.5


def test_recovery_memory_rejects_secret_evidence(tmp_path: Path):
    memory = IntelligentMemory(SQLiteMemoryStore(tmp_path / "memory.db"))
    assert not memory.record_recovery_outcome(
        "configure provider",
        "provider failed",
        "replan",
        False,
        "api_key=sk-abcdefghijklmnopqrstuvwxyz",
    )
