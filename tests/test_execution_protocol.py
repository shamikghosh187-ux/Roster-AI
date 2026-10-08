from roster.execution_protocol import ExecutionRequest, ExecutionResponse

def test_execution_response_success_preserves_request_identity():
    request = ExecutionRequest("task-1", "search", {"query": "python"}, "req-1")
    result = ExecutionResponse.success(request, ["a"])
    assert result.ok is True
    assert result.task_id == "task-1"
    assert result.request_id == "req-1"
    assert result.value == ["a"]

def test_execution_response_failure_is_structured():
    request = ExecutionRequest("task-2", "search")
    result = ExecutionResponse.failure(request, "denied")
    assert result.ok is False
    assert result.error == "denied"
