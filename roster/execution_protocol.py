"""Stable protocol objects for production task execution."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping

@dataclass(frozen=True)
class ExecutionRequest:
    task_id: str
    tool_name: str
    arguments: Mapping[str, Any] = field(default_factory=dict)
    request_id: str | None = None

@dataclass(frozen=True)
class ExecutionResponse:
    task_id: str
    ok: bool
    value: Any = None
    error: str | None = None
    request_id: str | None = None

    @classmethod
    def success(cls, request: ExecutionRequest, value: Any = None) -> "ExecutionResponse":
        return cls(request.task_id, True, value=value, request_id=request.request_id)

    @classmethod
    def failure(cls, request: ExecutionRequest, error: str) -> "ExecutionResponse":
        return cls(request.task_id, False, error=error, request_id=request.request_id)
