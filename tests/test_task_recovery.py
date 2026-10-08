from roster.task_recovery import recover

def test_recovery_returns_failure_without_leaking_exception():
    result=recover(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    assert not result.recovered and result.error=="boom"
