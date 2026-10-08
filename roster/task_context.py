from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class TaskContext:
    task_id: str
    request_id: str
    values: dict[str,Any]=field(default_factory=dict)
    def child(self,**values):
        merged=dict(self.values); merged.update(values)
        return TaskContext(self.task_id,self.request_id,merged)
