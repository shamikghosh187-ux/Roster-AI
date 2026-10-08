from roster.task_model import Task, TaskStatus

def test_task_defaults_to_pending():
    task=Task(name="research", input="find facts")
    assert task.status is TaskStatus.PENDING
    assert task.id

def test_task_status_transition_preserves_identity():
    task=Task(name="x").with_status(TaskStatus.RUNNING)
    assert task.status is TaskStatus.RUNNING
    assert task.name=="x"
