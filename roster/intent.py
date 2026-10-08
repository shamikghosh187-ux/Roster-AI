"""Typed intent representation for agent planning."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Intent:
    name: str
    confidence: float
    argument: str = ""
    def __post_init__(self):
        if not self.name.strip(): raise ValueError("intent name cannot be empty")
        if not 0 <= self.confidence <= 1: raise ValueError("confidence must be between 0 and 1")
