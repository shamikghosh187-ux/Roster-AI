from roster.task_store import SQLiteTaskStore
from roster.tasks import TaskEngine


def test_task_engine_restores_persisted_tasks(tmp_path):
    store = SQLiteTaskStore(tmp_path / "tasks.sqlite3")
    first = TaskEngine(store)
    task = first.create("Remember deployment")
    first.set_status(task.id, "done")

    second = TaskEngine(store)
    restored = second.list("done")
    assert len(restored) == 1
    assert restored[0].id == task.id


def test_task_engine_rejects_empty_titles(tmp_path):
    engine = TaskEngine(SQLiteTaskStore(tmp_path / "tasks.sqlite3"))
    try:
        engine.create("   ")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
