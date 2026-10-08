from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

class TaskStatus(str, Enum):
    PENDING="pending"
    PLANNING="planning"
    READY="ready"
    RUNNING="running"
    WAITING="waiting"
    COMPLETED="completed"
    FAILED="failed"
    CANCELLED="cancelled"

@dataclass(frozen=True)
class Task:
    id: str = field(default_factory=lambda: uuid4().hex)
    name: str = ""
    input: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def with_status(self, status: TaskStatus) -> "Task":
        return Task(self.id,self.name,self.input,status,self.priority,self.created_at,dict(self.metadata))
