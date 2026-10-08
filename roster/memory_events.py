"""Domain events emitted by memory operations."""
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class MemoryEvent:
    type: Literal["created","updated","deleted","conflict"]
    key: str
    source: str="memory"
