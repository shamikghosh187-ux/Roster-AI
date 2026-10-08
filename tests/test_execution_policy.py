import pytest
from roster.execution_policy import ExecutionPolicy

def test_execution_policy_validates_limits():
    assert ExecutionPolicy(max_parallel=3).max_parallel==3
    with pytest.raises(ValueError): ExecutionPolicy(max_parallel=0)
    with pytest.raises(ValueError): ExecutionPolicy(timeout_seconds=0)
