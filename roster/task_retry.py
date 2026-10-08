from dataclasses import dataclass
import time

@dataclass(frozen=True)
class TaskRetryPolicy:
    attempts: int = 3
    delay_seconds: float = 0.0
    def __post_init__(self):
        if self.attempts<1: raise ValueError("attempts must be positive")
        if self.delay_seconds<0: raise ValueError("delay cannot be negative")

def run_with_task_retry(operation,policy=None,sleep=time.sleep):
    policy=policy or TaskRetryPolicy(); last=None
    for attempt in range(policy.attempts):
        try: return operation()
        except Exception as exc:
            last=exc
            if attempt+1<policy.attempts and policy.delay_seconds: sleep(policy.delay_seconds)
    raise last
