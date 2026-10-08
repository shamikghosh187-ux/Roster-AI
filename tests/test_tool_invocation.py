from roster.tool_invocation import ToolInvocation

def test_invocation_normalizes_tool_name():
    invocation=ToolInvocation("  search  ",{"q":"python"}).normalized()
    assert invocation.tool_name=="search"
    assert invocation.arguments=={"q":"python"}
