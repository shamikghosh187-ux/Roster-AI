"""Bounded in-process event journal for diagnostics."""
from collections import deque
from dataclasses import dataclass
from threading import Lock
from typing import Any
@dataclass(frozen=True)
class EventRecord:
    name:str
    payload:dict[str,Any]
class EventJournal:
    def __init__(self,max_events:int=500):
        if max_events<1: raise ValueError("max_events must be positive")
        self._events=deque(maxlen=max_events); self._lock=Lock()
    def append(self,name:str,**payload:Any):
        if not name: raise ValueError("event name cannot be empty")
        with self._lock: self._events.append(EventRecord(name,dict(payload)))
    def snapshot(self):
        with self._lock: return list(self._events)
