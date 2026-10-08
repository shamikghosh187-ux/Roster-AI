from roster.task_retry import TaskRetryPolicy, run_with_task_retry

def test_retry_recovers_from_transient_failure():
    calls=[]
    def operation():
        calls.append(1)
        if len(calls)<2: raise RuntimeError("temporary")
        return "ok"
    assert run_with_task_retry(operation,TaskRetryPolicy(attempts=2))=="ok"
    assert len(calls)==2
