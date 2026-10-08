from copy import deepcopy
from dataclasses import dataclass,field
from datetime import datetime,timezone
from threading import RLock
from typing import Any,Callable

@dataclass(frozen=True)
class RuntimeEvent:
    name:str
    payload:dict[str,Any]=field(default_factory=dict)
    created_at:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("event name cannot be empty")
        if not isinstance(self.payload,dict):
            raise TypeError("event payload must be a dictionary")
        object.__setattr__(self,"payload",deepcopy(self.payload))

class EventBus:
    def __init__(self):
        self._subscribers={}
        self._lock=RLock()

    def subscribe(self,name,callback):
        if not name or not name.strip():
            raise ValueError("event name cannot be empty")
        if not callable(callback):
            raise TypeError("callback must be callable")
        with self._lock:
            callbacks=self._subscribers.setdefault(name,[])
            if callback not in callbacks:
                callbacks.append(callback)
        return callback

    def unsubscribe(self,name,callback):
        with self._lock:
            callbacks=self._subscribers.get(name)
            if not callbacks or callback not in callbacks:
                return False
            callbacks.remove(callback)
            if not callbacks:
                self._subscribers.pop(name,None)
            return True

    def emit(self,name,**payload):
        event=RuntimeEvent(name,payload)
        with self._lock:
            callbacks=tuple(self._subscribers.get(name,()))+tuple(self._subscribers.get("*",()))
        for callback in callbacks:
            try:
                callback(event)
            except Exception:
                continue
        return event
