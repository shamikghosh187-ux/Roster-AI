from roster.tool_catalog import ToolCatalog
from roster.tool_contract import ToolContract
from roster.tool_executor import ToolExecutor

def test_executor_invokes_registered_handler():
    catalog=ToolCatalog(); catalog.register(ToolContract("echo","Echo",handler=lambda args,ctx: args["value"],input_schema={"required":["value"]}))
    result=ToolExecutor(catalog).execute("echo",{"value":"ok"})
    assert result.ok and result.value=="ok"

def test_executor_reports_unknown_tool():
    result=ToolExecutor(catalog=ToolCatalog()).execute("missing",{})
    assert not result.ok
