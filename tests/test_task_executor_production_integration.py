from roster.execution_policy_resolver import ResolvedExecutionPolicy
from roster.production_tool_executor import ProductionToolExecutor
from roster.task_executor import TaskExecutor
from roster.task_model import Task, TaskStatus
from roster.tool_catalog import ToolCatalog
from roster.tool_contract import ToolContract

def test_task_executor_uses_production_invocation_contract():
    catalog=ToolCatalog()
    catalog.register(ToolContract("echo","Echo",handler=lambda args,ctx: ctx["value"]))
    production=ProductionToolExecutor(catalog,ResolvedExecutionPolicy())
    runner=TaskExecutor(production)
    task=Task(name="echo")
    result=runner.execute(task,"echo",{},context={"value":"integrated"})
    assert result.ok
    assert result.value=="integrated"
    assert runner.state.get(task.id).status is TaskStatus.COMPLETED
