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


def test_task_retry_does_not_retry_permanent_failure():
    from roster.retry import PermanentToolError
    import pytest
    calls=[]
    def operation(): calls.append(1); raise PermanentToolError("denied")
    with pytest.raises(PermanentToolError): run_with_task_retry(operation,TaskRetryPolicy(4))
    assert calls==[1]
