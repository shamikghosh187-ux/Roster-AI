from roster.task_store import SQLiteTaskStore
from roster.tasks import Task


def test_task_store_round_trip(tmp_path):
    store = SQLiteTaskStore(tmp_path / "tasks.sqlite3")
    task = Task("Ship release")
    store.save(task)
    loaded = store.get(task.id)
    assert loaded.title == "Ship release"
    assert loaded.status == "pending"


def test_task_store_filters_and_deletes(tmp_path):
    store = SQLiteTaskStore(tmp_path / "tasks.sqlite3")
    first = Task("First")
    second = Task("Second", status="done")
    store.save(first)
    store.save(second)
    assert [item.id for item in store.list("done")] == [second.id]
    assert store.delete(first.id) is True
    assert store.get(first.id) is None
