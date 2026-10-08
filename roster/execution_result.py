"""Normalized, explicit execution outcomes for production boundaries."""
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
    def ok(self): return self.status == "completed"
    @property
    def terminal(self): return self.status in {"completed","failed","denied","timeout","cancelled"}
    @classmethod
    def completed(cls, task_id, value=None, duration_ms=None): return cls(task_id,"completed",value=value,duration_ms=duration_ms)
    @classmethod
    def failed(cls, task_id, error, duration_ms=None): return cls(task_id,"failed",error=str(error)[:2000],duration_ms=duration_ms)
    @classmethod
    def denied(cls, task_id, reason, duration_ms=None): return cls(task_id,"denied",error=str(reason)[:500],duration_ms=duration_ms)
    @classmethod
    def timeout(cls, task_id, reason, duration_ms=None): return cls(task_id,"timeout",error=str(reason)[:500],duration_ms=duration_ms)
    @classmethod
    def cancelled(cls, task_id, reason="cancelled", duration_ms=None): return cls(task_id,"cancelled",error=str(reason)[:500],duration_ms=duration_ms)
