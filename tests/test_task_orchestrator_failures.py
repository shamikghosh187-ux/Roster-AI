import pytest
from roster.task_model import Task
from roster.task_orchestrator import TaskOrchestrator
from roster.task_plan import TaskPlan

class FailedResult:
    ok=False
    error="tool failed"

def test_orchestrator_does_not_mark_failed_step_completed():
    task=Task(name="bad")
    trace=TaskOrchestrator(lambda step: FailedResult())
    with pytest.raises(RuntimeError,match="tool failed"):
        trace.run(TaskPlan().add(task))
    phases=[r.phase for r in trace.trace.records()]
    assert phases==["started","failed"]

def test_orchestrator_records_exception_as_failure():
    task=Task(name="bad")
    trace=TaskOrchestrator(lambda step: (_ for _ in ()).throw(ValueError("boom")))
    with pytest.raises(ValueError):
        trace.run(TaskPlan().add(task))
    assert trace.trace.records()[-1].phase=="failed"
