import pytest
from roster.task_lifecycle import InvalidTaskTransition, can_transition, transition
from roster.task_model import TaskStatus

def test_running_can_complete():
    assert can_transition(TaskStatus.RUNNING,TaskStatus.COMPLETED)
    assert transition(TaskStatus.RUNNING,TaskStatus.COMPLETED) is TaskStatus.COMPLETED

def test_terminal_state_cannot_restart():
    with pytest.raises(InvalidTaskTransition): transition(TaskStatus.COMPLETED,TaskStatus.RUNNING)
