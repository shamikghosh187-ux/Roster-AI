from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

@dataclass
class TraceEvent:
    event: str
    data: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ExecutionTrace:
    def __init__(self):
        self.events: list[TraceEvent] = []
    def record(self, event: str, **data):
        item = TraceEvent(event=event, data=data)
        self.events.append(item)
        return item
    def clear(self):
        self.events.clear()
    def as_dicts(self):
        return [{"event": e.event, "data": e.data, "created_at": e.created_at} for e in self.events]
