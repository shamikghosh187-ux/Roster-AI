"""Deterministic aggregate summary for workflow execution."""
from __future__ import annotations
from dataclasses import dataclass

_KNOWN={"completed","failed","cancelled"}

@dataclass(frozen=True)
class ExecutionSummary:
    total:int
    completed:int
    failed:int
    cancelled:int
    @property
    def success_rate(self):
        return self.completed / self.total if self.total else 0.0

def summarize(results):
    statuses=[getattr(item,"status",None) for item in results]
    unknown=[status for status in statuses if status not in _KNOWN]
    if unknown:
        raise ValueError(f"unknown execution statuses: {unknown}")
    return ExecutionSummary(
        len(statuses),
        statuses.count("completed"),
        statuses.count("failed"),
        statuses.count("cancelled"),
    )
