"""Idempotent lifecycle state machine for application services."""
from enum import Enum
from threading import Lock
class LifecycleState(str,Enum):
    CREATED="created"; RUNNING="running"; STOPPING="stopping"; STOPPED="stopped"
class Lifecycle:
    def __init__(self): self._state=LifecycleState.CREATED; self._lock=Lock()
    @property
    def state(self):
        with self._lock: return self._state
    def start(self):
        with self._lock:
            if self._state!=LifecycleState.CREATED: return False
            self._state=LifecycleState.RUNNING; return True
    def stop(self):
        with self._lock:
            if self._state==LifecycleState.STOPPED: return False
            self._state=LifecycleState.STOPPED if self._state==LifecycleState.CREATED else LifecycleState.STOPPING
            if self._state==LifecycleState.STOPPING: self._state=LifecycleState.STOPPED
            return True
