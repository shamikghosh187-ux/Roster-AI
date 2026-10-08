from roster.task_model import Task, TaskStatus
from roster.task_executor import TaskExecutor
from roster.tool_catalog import ToolCatalog
from roster.tool_contract import ToolContract
from roster.tool_executor import ToolExecutor

def test_task_executor_updates_lifecycle():
    catalog=ToolCatalog(); catalog.register(ToolContract("echo","Echo",handler=lambda args,ctx: args["value"],input_schema={"required":["value"]}))
    task=Task(name="echo")
    result=TaskExecutor(ToolExecutor(catalog)).execute(task,"echo",{"value":"done"})
    assert result.ok
    assert task.id and len(TaskExecutor(ToolExecutor(catalog)).events)==0
