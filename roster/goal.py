"""Typed user goal state for multi-step agent work."""
from dataclasses import dataclass, field

@dataclass
class Goal:
    objective: str
    completed: bool = False
    metadata: dict = field(default_factory=dict)
    def complete(self): self.completed=True
