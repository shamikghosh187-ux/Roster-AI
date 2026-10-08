from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

@dataclass(frozen=True)
class TaskEvent:
    task_id: str
    name: str
    payload: dict[str,Any]
    created_at: str

def make_task_event(task_id,name,**payload):
    return TaskEvent(task_id,name,payload,datetime.now(timezone.utc).isoformat())
