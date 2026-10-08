"""Explicit timeout policy used by execution adapters."""
from dataclasses import dataclass
@dataclass(frozen=True)
class TimeoutPolicy:
    seconds: float = 30.0
    def __post_init__(self):
        if self.seconds <= 0: raise ValueError("timeout must be positive")
