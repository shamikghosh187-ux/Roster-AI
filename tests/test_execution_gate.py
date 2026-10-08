from roster.execution_gate import ExecutionGate
from roster.execution_policy_resolver import ResolvedExecutionPolicy

def test_sensitive_action_requires_confirmation():
    gate=ExecutionGate(ResolvedExecutionPolicy(confirmation_required=True))
    decision=gate.check(sensitive=True)
    assert decision.allowed is False
    assert decision.requires_confirmation is True

def test_confirmed_sensitive_action_is_allowed():
    gate=ExecutionGate(ResolvedExecutionPolicy(confirmation_required=True))
    assert gate.check(sensitive=True, confirmed=True).allowed is True
