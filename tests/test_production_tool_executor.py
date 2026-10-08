import pytest
from roster.execution_policy_resolver import ResolvedExecutionPolicy
from roster.production_tool_executor import ProductionToolExecutor
from roster.tool_catalog import ToolCatalog
from roster.tool_contract import ToolContract
import time

def make_catalog(sensitive=False, handler=None):
    catalog=ToolCatalog()
    catalog.register(ToolContract("echo","echo",input_schema={},sensitive=sensitive,handler=handler or (lambda args,ctx:"ok")))
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

def test_executor_enforces_configured_timeout():
    def slow(args,ctx):
        time.sleep(0.05)
        return "late"
    policy=ResolvedExecutionPolicy(timeout_seconds=0.001)
    result=ProductionToolExecutor(make_catalog(handler=slow),policy).execute("t1","echo")
    assert result.ok is False
    assert "exceeded" in result.error


def test_executor_preserves_cancellation():
    from roster.cancel import CancellationToken, CancelledError
    token=CancellationToken(); token.cancel()
    with pytest.raises(CancelledError):
        ProductionToolExecutor(make_catalog(),ResolvedExecutionPolicy()).execute("t1","echo",cancellation=token)

def test_executor_passes_context_to_handler():
    seen=[]
    def handler(args,ctx):
        seen.append(ctx); return "ok"
    result=ProductionToolExecutor(make_catalog(handler=handler),ResolvedExecutionPolicy()).execute("t1","echo",context={"request_id":"r1"})
    assert result.ok
    assert seen == [{"request_id":"r1"}]
