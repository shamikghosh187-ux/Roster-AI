"""Small observer boundary for memory domain events."""
from collections.abc import Callable
from roster.memory_events import MemoryEvent

class MemoryObserver:
    def __init__(self): self._listeners:list[Callable[[MemoryEvent],None]]=[]
    def subscribe(self,listener): self._listeners.append(listener); return listener
    def emit(self,event):
        for listener in tuple(self._listeners): listener(event)
