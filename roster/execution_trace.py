from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class ExecutionRecord:
    task_id: str
    phase: str
    detail: str = ""
    created_at: str = ""
    def __post_init__(self):
        if not self.created_at: object.__setattr__(self,"created_at",datetime.now(timezone.utc).isoformat())

class ExecutionTrace:
    def __init__(self): self._records=[]
    def record(self,task_id,phase,detail=""):
        item=ExecutionRecord(task_id,phase,detail); self._records.append(item); return item
    def records(self): return tuple(self._records)
