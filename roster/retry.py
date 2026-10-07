"""Small dependency-free retry policy."""
from dataclasses import dataclass
from typing import Callable, TypeVar
T = TypeVar("T")
@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3
    delay_seconds: float = 0.0
    def __post_init__(self):
        if self.attempts < 1: raise ValueError("attempts must be at least 1")
        if self.delay_seconds < 0: raise ValueError("delay_seconds cannot be negative")
def run_with_retry(operation: Callable[[], T], policy: RetryPolicy, sleep: Callable[[float], None] | None = None) -> T:
    sleeper = sleep or __import__("time").sleep
    last_error = None
    for attempt in range(policy.attempts):
        try: return operation()
        except Exception as exc:
            last_error = exc
            if attempt + 1 < policy.attempts: sleeper(policy.delay_seconds)
    raise last_error
