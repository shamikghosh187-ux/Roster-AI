from roster.execution_result import NormalizedExecutionResult
from roster.execution_summary import summarize

def test_summary_counts_execution_statuses():
    summary=summarize([NormalizedExecutionResult.completed("a"),NormalizedExecutionResult.failed("b","x"),NormalizedExecutionResult.completed("c")])
    assert summary.total == 3
    assert summary.completed == 2
    assert summary.failed == 1
    assert summary.success_rate == 2/3


def test_empty_summary_has_zero_success_rate():
    assert summarize([]).success_rate==0.0

def test_summary_rejects_unknown_status():
    class Result: status="running"
    import pytest
    with pytest.raises(ValueError): summarize([Result()])
