import pytest
from roster.circuit_breaker import CircuitBreaker,CircuitOpenError
def test_circuit_opens_at_threshold():
    b=CircuitBreaker(2); b.record_failure(); b.allow(); b.record_failure()
    with pytest.raises(CircuitOpenError): b.allow()
def test_success_resets_circuit():
    b=CircuitBreaker(1); b.record_failure(); b.record_success(); b.allow()
    assert b.state.failures==0
