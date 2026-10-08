from roster.execution_policy_resolver import ResolvedExecutionPolicy
from roster.production_tool_executor import ProductionToolExecutor
from roster.tool_catalog import ToolCatalog
from roster.tool_contract import ToolContract

def make_catalog(sensitive=False):
    catalog=ToolCatalog()
    catalog.register(ToolContract("echo","echo",input_schema={},sensitive=sensitive,handler=lambda args,ctx:"ok"))
    return catalog

def test_executor_runs_registered_tool():
    result=ProductionToolExecutor(make_catalog(),ResolvedExecutionPolicy()).execute("t1","echo")
    assert result.ok is True
    assert result.value == "ok"

def test_executor_blocks_sensitive_tool_without_confirmation():
    result=ProductionToolExecutor(make_catalog(True),ResolvedExecutionPolicy()).execute("t1","echo")
    assert result.ok is False
    assert result.error == "confirmation required"

def test_executor_reports_unknown_tool():
    result=ProductionToolExecutor(make_catalog(),ResolvedExecutionPolicy()).execute("t1","missing")
    assert result.ok is False
    assert "unknown tool" in result.error
