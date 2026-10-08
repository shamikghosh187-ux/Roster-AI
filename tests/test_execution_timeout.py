import pytest
from roster.execution_errors import ExecutionTimeout
from roster.execution_timeout import run_with_timeout

def test_timeout_boundary_returns_fast_operation():
    assert run_with_timeout(lambda: "ok",1)=="ok"

def test_timeout_boundary_raises_for_slow_operation():
    import time
    with pytest.raises(ExecutionTimeout): run_with_timeout(lambda: time.sleep(0.05),0.001)
