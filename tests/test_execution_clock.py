from roster.execution_clock import ExecutionClock

def test_clock_measures_elapsed_time():
    values=iter([10.0, 10.125])
    clock=ExecutionClock(lambda: next(values))
    started=clock.now()
    assert clock.elapsed_ms(started) == 125.0
