"""Structured retrieval result with optional citation."""
from dataclasses import dataclass
from roster.citation import Citation

@dataclass(frozen=True)
class RetrievalResult:
    text: str
    score: float
    citation: Citation|None = None
    def __post_init__(self):
        if not 0 <= self.score <= 1: raise ValueError("score must be between 0 and 1")
