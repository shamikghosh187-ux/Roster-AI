from dataclasses import dataclass
from roster.task_retry import TaskRetryPolicy, run_with_task_retry

@dataclass(frozen=True)
class RecoveryResult:
    recovered: bool
    value: object = None
    error: str | None = None

def recover(operation,policy=None):
    try: return RecoveryResult(True,run_with_task_retry(operation,policy))
    except Exception as exc: return RecoveryResult(False,error=str(exc))
