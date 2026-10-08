import pytest
from roster.cancel import CancellationToken, CancelledError
from roster.task_executor import TaskExecutor
from roster.task_model import Task, TaskStatus
from roster.tool_catalog import ToolCatalog
from roster.tool_contract import ToolContract
from roster.tool_executor import ToolExecutor

def make_executor(handler):
    catalog=ToolCatalog()
    catalog.register(ToolContract("echo","Echo",handler=handler))
    return TaskExecutor(ToolExecutor(catalog))

def test_task_executor_marks_failure_when_tool_raises():
    runner=make_executor(lambda args,ctx: (_ for _ in ()).throw(RuntimeError("boom")))
    task=Task(name="echo")
    result=runner.execute(task,"echo",{})
    assert result.ok is False
    assert runner.state.get(task.id).status is TaskStatus.FAILED
    assert runner.events[-1].name=="failed"
    assert runner.events[-1].payload["error"]=="boom"

def test_task_executor_does_not_leave_cancelled_task_running():
    token=CancellationToken()
    def handler(args,ctx):
        token.raise_if_cancelled()
    token.cancel()
    runner=make_executor(handler)
    task=Task(name="echo")
    with pytest.raises(CancelledError):
        runner.execute(task,"echo",{})
    assert runner.state.get(task.id).status is TaskStatus.CANCELLED
    assert runner.events[-1].name=="cancelled"
