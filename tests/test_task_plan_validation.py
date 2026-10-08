import pytest
from roster.task_graph_validation import TaskGraphError
from roster.task_model import Task
from roster.task_plan import TaskPlan

def test_plan_rejects_missing_dependency():
    with pytest.raises(TaskGraphError,match="missing dependencies"):
        TaskPlan().add(Task(name="job"),["missing"])

def test_plan_rejects_duplicate_task_ids():
    task=Task(name="job")
    with pytest.raises(TaskGraphError,match="duplicate"):
        TaskPlan().add(task).add(task)

def test_plan_validation_is_available_before_execution():
    plan=TaskPlan().add(Task(name="job"))
    assert plan.validate() is plan
