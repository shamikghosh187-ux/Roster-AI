"""Normalized result envelope for orchestration boundaries."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class NormalizedExecutionResult:
    task_id: str
    status: str
    value: Any = None
    error: str | None = None
    duration_ms: float | None = None

    @property
    def ok(self) -> bool:
        return self.status == "completed"

    @classmethod
    def completed(cls, task_id: str, value: Any = None, duration_ms: float | None = None):
        return cls(task_id, "completed", value=value, duration_ms=duration_ms)

    @classmethod
    def failed(cls, task_id: str, error: str, duration_ms: float | None = None):
        return cls(task_id, "failed", error=error, duration_ms=duration_ms)
