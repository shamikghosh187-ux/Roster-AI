from dataclasses import dataclass
from threading import RLock
from roster.task_lifecycle import transition
from roster.task_model import Task, TaskStatus

@dataclass
class TaskStateStore:
    _tasks: dict[str,Task]
    def __init__(self):
        self._tasks={}
        self._lock=RLock()

    def add(self,task):
        with self._lock:
            if task.id in self._tasks: raise ValueError(f"task already exists: {task.id}")
            snapshot=Task(task.id,task.name,task.input,task.status,task.priority,task.created_at,dict(task.metadata))
            self._tasks[task.id]=snapshot
            return snapshot

    def get(self,task_id):
        with self._lock:
            return self._tasks.get(task_id)

    def move(self,task_id,status):
        with self._lock:
            task=self._tasks[task_id]
            updated=task.with_status(transition(task.status,status))
            self._tasks[task_id]=updated
            return updated

    def all(self):
        with self._lock:
            return tuple(self._tasks.values())
