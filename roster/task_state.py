from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from roster.task_lifecycle import transition
from roster.task_model import Task

@dataclass
class TaskStateStore:
    _tasks: dict[str,Task]

    def __init__(self):
        self._tasks={}
        self._lock=RLock()

    @staticmethod
    def _snapshot(task):
        return Task(task.id,task.name,task.input,task.status,task.priority,task.created_at,deepcopy(task.metadata))

    def add(self,task):
        if not isinstance(task,Task):
            raise TypeError("task must be a Task")
        with self._lock:
            if task.id in self._tasks:
                raise ValueError(f"task already exists: {task.id}")
            snapshot=self._snapshot(task)
            self._tasks[task.id]=snapshot
            return self._snapshot(snapshot)

    def get(self,task_id):
        with self._lock:
            task=self._tasks.get(task_id)
            return None if task is None else self._snapshot(task)

    def move(self,task_id,status):
        with self._lock:
            task=self._tasks[task_id]
            updated=task.with_status(transition(task.status,status))
            self._tasks[task_id]=updated
            return self._snapshot(updated)

    def all(self):
        with self._lock:
            return tuple(self._snapshot(task) for task in self._tasks.values())
