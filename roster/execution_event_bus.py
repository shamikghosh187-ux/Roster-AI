"""In-process event sink with bounded subscriber failures."""
from __future__ import annotations
from typing import Callable

class ExecutionEventBus:
    def __init__(self): self._subscribers=[]
    def subscribe(self, callback: Callable): self._subscribers.append(callback); return callback
    def publish(self,event):
        failures=[]
        for callback in tuple(self._subscribers):
            try: callback(event)
            except Exception as exc: failures.append(exc)
        return tuple(failures)
