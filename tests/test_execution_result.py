from roster.execution_result import NormalizedExecutionResult

def test_completed_result_is_successful():
    result=NormalizedExecutionResult.completed("t1", "ok", 1.5)
    assert result.ok is True
    assert result.value == "ok"
    assert result.duration_ms == 1.5

def test_failed_result_is_not_successful():
    result=NormalizedExecutionResult.failed("t1", "boom")
    assert result.ok is False
    assert result.error == "boom"
