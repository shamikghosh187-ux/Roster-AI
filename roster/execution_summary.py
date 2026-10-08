"""Deterministic aggregate summary for workflow execution."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionSummary:
    total: int
    completed: int
    failed: int
    cancelled: int
    @property
    def success_rate(self):
        return self.completed / self.total if self.total else 1.0

def summarize(results):
    statuses=[getattr(item,"status",None) for item in results]
    return ExecutionSummary(len(statuses),statuses.count("completed"),statuses.count("failed"),statuses.count("cancelled"))
