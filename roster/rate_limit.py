"""Thread-safe sliding-window request limiter."""
from collections import deque
from threading import Lock
from time import monotonic
class RateLimiter:
    def __init__(self,limit:int,window_seconds:float):
        if limit<1 or window_seconds<=0: raise ValueError("invalid rate limit configuration")
        self.limit=limit; self.window_seconds=window_seconds; self._events=deque(); self._lock=Lock()
    def allow(self):
        now=monotonic()
        with self._lock:
            cutoff=now-self.window_seconds
            while self._events and self._events[0]<=cutoff: self._events.popleft()
            if len(self._events)>=self.limit: return False
            self._events.append(now); return True
    def remaining(self):
        now=monotonic()
        with self._lock:
            cutoff=now-self.window_seconds
            while self._events and self._events[0]<=cutoff: self._events.popleft()
            return max(0,self.limit-len(self._events))
