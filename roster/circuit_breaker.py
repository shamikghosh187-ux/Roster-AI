"""Failure isolation for repeatedly failing integrations."""
from dataclasses import dataclass
from threading import Lock
class CircuitOpenError(RuntimeError): pass
@dataclass(frozen=True)
class CircuitState:
    failures:int
    open:bool
class CircuitBreaker:
    def __init__(self, threshold:int=3):
        if threshold<1: raise ValueError("threshold must be positive")
        self._threshold=threshold; self._failures=0; self._open=False; self._lock=Lock()
    @property
    def state(self):
        with self._lock: return CircuitState(self._failures,self._open)
    def allow(self):
        with self._lock:
            if self._open: raise CircuitOpenError("circuit is open")
    def record_success(self):
        with self._lock: self._failures=0; self._open=False
    def record_failure(self):
        with self._lock:
            self._failures+=1
            if self._failures>=self._threshold: self._open=True
