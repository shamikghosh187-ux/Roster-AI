import pytest
from roster.task_model import Task, TaskStatus
from roster.task_state import TaskStateStore

def test_state_store_updates_task_status():
    store=TaskStateStore(); task=store.add(Task(name="job"))
    store.move(task.id,TaskStatus.PLANNING)
    assert store.get(task.id).status is TaskStatus.PLANNING

def test_duplicate_tasks_are_rejected():
    store=TaskStateStore(); task=Task(name="job"); store.add(task)
    with pytest.raises(ValueError): store.add(task)
