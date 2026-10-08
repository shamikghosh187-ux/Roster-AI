"""Addressable chunk of source content."""
from dataclasses import dataclass

@dataclass(frozen=True)
class KnowledgeChunk:
    source_id: str
    index: int
    text: str
    def __post_init__(self):
        if self.index < 0: raise ValueError("chunk index cannot be negative")
