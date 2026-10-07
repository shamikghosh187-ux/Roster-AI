"""Dependency-free retry policies with backwards-compatible tool errors."""
from dataclasses import dataclass
from typing import Callable, TypeVar
import time
T=TypeVar("T")
class TransientToolError(Exception): pass
class PermanentToolError(Exception): pass
@dataclass(frozen=True)
class RetryPolicy:
    attempts:int=3
    delay_seconds:float=0.0
    def __post_init__(self):
        if self.attempts<1: raise ValueError("attempts must be at least 1")
        if self.delay_seconds<0: raise ValueError("delay_seconds cannot be negative")
    def run(self,fn:Callable[[],T])->T:
        for attempt in range(self.attempts):
            try: return fn()
            except TransientToolError:
                if attempt+1==self.attempts: raise
                if self.delay_seconds: time.sleep(self.delay_seconds)
def run_with_retry(operation:Callable[[],T],policy:RetryPolicy,sleep:Callable[[float],None]|None=None)->T:
    sleeper=sleep or time.sleep
    last_error=None
    for attempt in range(policy.attempts):
        try: return operation()
        except Exception as exc:
            last_error=exc
            if attempt+1<policy.attempts: sleeper(policy.delay_seconds)
    assert last_error is not None
    raise last_error
