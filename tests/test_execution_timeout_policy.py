import pytest
from roster.execution_timeout_policy import TimeoutPolicy

def test_timeout_policy_requires_positive_duration():
    assert TimeoutPolicy(2).seconds == 2
    with pytest.raises(ValueError): TimeoutPolicy(0)
