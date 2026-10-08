"""Thread-safe in-process execution event bus."""
from __future__ import annotations
from threading import RLock
from typing import Callable

class ExecutionEventBus:
    def __init__(self):
        self._subscribers=[]
        self._lock=RLock()

    def subscribe(self,callback:Callable):
        if not callable(callback): raise TypeError("subscriber must be callable")
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)
        return callback

    def unsubscribe(self,callback):
        with self._lock:
            try: self._subscribers.remove(callback)
            except ValueError: return False
            return True

    def publish(self,event):
        with self._lock:
            subscribers=tuple(self._subscribers)
        failures=[]
        for callback in subscribers:
            try: callback(event)
            except Exception as exc: failures.append(exc)
        return tuple(failures)

    def subscriber_count(self):
        with self._lock: return len(self._subscribers)
