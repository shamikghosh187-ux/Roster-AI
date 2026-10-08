import pytest
from roster.cancel import CancellationToken, CancelledError
from roster.task_retry import TaskRetryPolicy, run_with_task_retry

def test_retry_preserves_cancellation():
    token=CancellationToken(); token.cancel(); calls=[]
    def operation():
        calls.append(1); token.raise_if_cancelled()
    with pytest.raises(CancelledError):
        run_with_task_retry(operation,TaskRetryPolicy(3))
    assert len(calls)==1
