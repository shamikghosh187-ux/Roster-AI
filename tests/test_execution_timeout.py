import pytest, time
from roster.execution_timeout import ExecutionTimedOut,run_with_timeout
from roster.execution_timeout_policy import TimeoutPolicy

def test_timeout_adapter_returns_fast_operation(): assert run_with_timeout(lambda:"ok",TimeoutPolicy(.5))=="ok"
def test_timeout_adapter_raises_for_slow_operation():
    with pytest.raises(ExecutionTimedOut): run_with_timeout(lambda:time.sleep(.05),TimeoutPolicy(.001))
