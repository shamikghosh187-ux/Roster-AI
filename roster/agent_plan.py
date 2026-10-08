"""Immutable agent plan containing ordered subtasks."""
from dataclasses import dataclass
from roster.subtask import Subtask

@dataclass(frozen=True)
class AgentPlan:
    goal: str
    steps: tuple[Subtask,...]
    def ids(self): return tuple(step.id for step in self.steps)
