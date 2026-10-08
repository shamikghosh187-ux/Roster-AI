from roster.retry import RetryPolicy, run_with_retry
def test_retry_recovers_after_transient_failures():
    calls=[]
    def operation():
        calls.append(1)
        if len(calls)<3: raise RuntimeError("temporary")
        return "ok"
    assert run_with_retry(operation, RetryPolicy(3), sleep=lambda _: None)=="ok"
    assert len(calls)==3


def test_retry_policy_reraises_transient_failure_instead_of_returning_none():
    from roster.retry import TransientToolError
    import pytest
    with pytest.raises(TransientToolError):
        RetryPolicy(2).run(lambda: (_ for _ in ()).throw(TransientToolError("temporary")))

def test_retry_policy_does_not_retry_permanent_failure():
    from roster.retry import PermanentToolError
    import pytest
    calls=[]
    def operation():
        calls.append(1); raise PermanentToolError("permanent")
    with pytest.raises(PermanentToolError): RetryPolicy(5).run(operation)
    assert calls==[1]

def test_generic_retry_preserves_cancellation():
    from roster.cancel import CancellationToken, CancelledError
    import pytest
    token=CancellationToken(); token.cancel(); calls=[]
    def operation(): calls.append(1); token.raise_if_cancelled()
    with pytest.raises(CancelledError): run_with_retry(operation,RetryPolicy(5),sleep=lambda _:None)
    assert calls==[1]
