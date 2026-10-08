from dataclasses import dataclass
from roster.task_lifecycle import transition
from roster.task_model import Task, TaskStatus

@dataclass
class TaskStateStore:
    _tasks: dict[str,Task]
    def __init__(self): self._tasks={}
    def add(self,task):
        if task.id in self._tasks: raise ValueError(f"task already exists: {task.id}")
        self._tasks[task.id]=task; return task
    def get(self,task_id): return self._tasks.get(task_id)
    def move(self,task_id,status):
        task=self._tasks[task_id]
        updated=task.with_status(transition(task.status,status))
        self._tasks[task_id]=updated
        return updated
    def all(self): return tuple(self._tasks.values())
