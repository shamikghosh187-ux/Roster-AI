import time
from roster.execution_policy_resolver import ResolvedExecutionPolicy
from roster.execution_result import NormalizedExecutionResult
from roster.production_tool_executor import ProductionToolExecutor
from roster.storage import SQLiteMemoryStore
from roster.tool_catalog import ToolCatalog
from roster.tool_contract import ToolContract

def catalog(handler=None,sensitive=False):
    c=ToolCatalog(); c.register(ToolContract("echo","echo",input_schema={},sensitive=sensitive,handler=handler or (lambda a,x:"ok"))); return c

def test_denied_has_explicit_status():
    r=ProductionToolExecutor(catalog(sensitive=True),ResolvedExecutionPolicy()).execute("t","echo")
    assert r.status=="denied" and not r.ok

def test_timeout_has_explicit_status():
    def slow(a,x): time.sleep(.05); return "late"
    r=ProductionToolExecutor(catalog(slow),ResolvedExecutionPolicy(timeout_seconds=.001)).execute("t","echo")
    assert r.status=="timeout"

def test_telemetry_failure_cannot_break_execution():
    events=[]
    def observer(event,data):
        events.append(event); raise RuntimeError("telemetry down")
    r=ProductionToolExecutor(catalog(),ResolvedExecutionPolicy(),observer=observer).execute("t","echo")
    assert r.ok and events[0]=="execution_started"

def test_error_text_is_bounded():
    def broken(a,x): raise RuntimeError("x"*10000)
    r=ProductionToolExecutor(catalog(broken),ResolvedExecutionPolicy()).execute("t","echo")
    assert r.status=="failed" and len(r.error)<=2000

def test_clear_removes_recovery_history(tmp_path):
    s=SQLiteMemoryStore(tmp_path/"memory.db"); s.record_recovery_experience("g","f","retry",True,"ok"); s.clear()
    assert s.recovery_stats("g","f","retry")== (0,0)
