from roster.retry import RetryPolicy, run_with_retry
def test_retry_recovers_after_transient_failures():
    calls=[]
    def operation():
        calls.append(1)
        if len(calls)<3: raise RuntimeError("temporary")
        return "ok"
    assert run_with_retry(operation, RetryPolicy(3), sleep=lambda _: None)=="ok"
    assert len(calls)==3
