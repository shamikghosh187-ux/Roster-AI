"""Declarative query object for memory retrieval."""
from dataclasses import dataclass

@dataclass(frozen=True)
class MemoryQuery:
    text: str = ""
    kind: str|None = None
    minimum_score: float = 0.0
    limit: int = 10
    def __post_init__(self):
        if not 0 <= self.minimum_score <= 1: raise ValueError("minimum_score must be between 0 and 1")
        if self.limit < 1: raise ValueError("limit must be positive")
