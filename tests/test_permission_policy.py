from roster.execution_policy import ConfirmationMode
from roster.permission_policy import PermissionPolicy

def test_sensitive_action_requires_confirmation_in_smart_mode():
    decision=PermissionPolicy().evaluate(sensitive=True)
    assert decision.allowed and decision.requires_confirmation

def test_never_mode_skips_confirmation():
    assert not PermissionPolicy(ConfirmationMode.NEVER).evaluate(True).requires_confirmation
