from dataclasses import dataclass
from roster.execution_policy import ConfirmationMode

@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str

class PermissionPolicy:
    def __init__(self,mode=ConfirmationMode.SMART,sensitive_requires_confirmation=True):
        self.mode=mode; self.sensitive_requires_confirmation=sensitive_requires_confirmation
    def evaluate(self,sensitive=False):
        if self.mode is ConfirmationMode.NEVER: return PermissionDecision(True,False,"confirmation disabled by policy")
        if self.mode is ConfirmationMode.ALWAYS: return PermissionDecision(True,True,"confirmation required by policy")
        if sensitive and self.sensitive_requires_confirmation: return PermissionDecision(True,True,"sensitive action requires confirmation")
        return PermissionDecision(True,False,"action allowed")
