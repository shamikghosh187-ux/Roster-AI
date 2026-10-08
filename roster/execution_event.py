"""Typed execution events for observability adapters."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ExecutionEvent:
    kind: str
    request_id: str
    task_id: str | None = None
    payload: dict[str,Any] | None = None

    def as_dict(self):
        return {"kind":self.kind,"request_id":self.request_id,"task_id":self.task_id,"payload":self.payload or {}}
