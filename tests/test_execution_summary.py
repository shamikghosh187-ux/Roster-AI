from roster.execution_result import NormalizedExecutionResult
from roster.execution_summary import summarize

def test_summary_counts_execution_statuses():
    summary=summarize([NormalizedExecutionResult.completed("a"),NormalizedExecutionResult.failed("b","x"),NormalizedExecutionResult.completed("c")])
    assert summary.total == 3
    assert summary.completed == 2
    assert summary.failed == 1
    assert summary.success_rate == 2/3
