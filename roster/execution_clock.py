"""Injectable monotonic clock for execution measurements."""
from __future__ import annotations
import time

class ExecutionClock:
    def __init__(self, clock=time.monotonic):
        self._clock=clock
    def now(self) -> float:
        return self._clock()
    def elapsed_ms(self, started: float) -> float:
        return max(0.0, (self.now()-started)*1000.0)
