from roster.tool_result import ToolResult

def test_tool_result_success():
    result=ToolResult.success({"answer":42})
    assert result.ok and result.value["answer"]==42

def test_tool_result_failure_can_be_retryable():
    result=ToolResult.failure("temporary",retryable=True)
    assert not result.ok and result.retryable
