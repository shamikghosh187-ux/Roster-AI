"""Explicit retry policy used by execution adapters."""
from dataclasses import dataclass
@dataclass(frozen=True)
class ExecutionRetryPolicy:
    attempts:int=1; delay_seconds:float=0.0
    def __post_init__(self):
        if self.attempts<1: raise ValueError("attempts must be positive")
        if self.delay_seconds<0: raise ValueError("delay cannot be negative")
