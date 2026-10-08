"""Request-scoped execution context without coupling to the UI."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class ExecutionContext:
    request_id: str
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def child(self, **metadata: Any) -> "ExecutionContext":
        merged = dict(self.metadata)
        merged.update(metadata)
        return ExecutionContext(self.request_id, self.session_id, merged)
