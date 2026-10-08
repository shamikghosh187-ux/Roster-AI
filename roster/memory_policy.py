"""Retention and privacy policy for durable memory."""
from dataclasses import dataclass

@dataclass(frozen=True)
class MemoryPolicy:
    enabled: bool = True
    retention_days: int = 90
    minimum_confidence: float = 0.0
    allow_preferences: bool = True
    allow_profile: bool = True

    def __post_init__(self):
        if self.retention_days < 0: raise ValueError("retention_days cannot be negative")
        if not 0 <= self.minimum_confidence <= 1: raise ValueError("minimum_confidence must be between 0 and 1")

    def accepts(self, confidence: float, kind: str) -> bool:
        if not self.enabled or confidence < self.minimum_confidence: return False
        if kind == "preference" and not self.allow_preferences: return False
        if kind == "profile" and not self.allow_profile: return False
        return True
