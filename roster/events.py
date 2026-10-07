from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

@dataclass(frozen=True)
class RuntimeEvent:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable[[RuntimeEvent], None]]] = {}

    def subscribe(self, name: str, callback: Callable[[RuntimeEvent], None]):
        self._subscribers.setdefault(name, []).append(callback)

    def emit(self, name: str, **payload):
        event = RuntimeEvent(name, payload)
        for callback in tuple(self._subscribers.get(name, [])):
            try:
                callback(event)
            except Exception:
                continue
        for callback in tuple(self._subscribers.get("*", [])):
            try:
                callback(event)
            except Exception:
                continue
        return event
