"""Explainable decision object emitted before agent execution."""
from dataclasses import dataclass

@dataclass(frozen=True)
class AgentDecision:
    action: str
    confidence: float
    requires_confirmation: bool = False
    rationale: str = ""
