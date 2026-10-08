from dataclasses import dataclass
from roster.task_model import Task

@dataclass(frozen=True)
class PriorityPolicy:
    minimum: int = -100
    maximum: int = 100
    def validate(self,value:int)->int:
        value=int(value)
        if not self.minimum <= value <= self.maximum: raise ValueError("task priority outside policy range")
        return value

def prioritize(tasks, policy=None):
    policy=policy or PriorityPolicy()
    return tuple(sorted(tasks,key=lambda task:(-policy.validate(task.priority),task.created_at,task.id)))
