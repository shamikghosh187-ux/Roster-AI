"""Small policy gate used before a task enters a tool executor."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class GateDecision:
    allowed: bool
    reason: str
    requires_confirmation: bool = False

class ExecutionGate:
    def __init__(self, policy):
        self.policy = policy

    def check(self, *, sensitive: bool = False, confirmed: bool = False) -> GateDecision:
        if sensitive and self.policy.confirmation_required and not confirmed:
            return GateDecision(False, "confirmation required", True)
        return GateDecision(True, "allowed")
