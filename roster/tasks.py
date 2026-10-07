from dataclasses import dataclass, field
import uuid


@dataclass
class Task:
    title: str
    status: str = "pending"
    id: str = field(default_factory=lambda: uuid.uuid4().hex)


class TaskEngine:
    def __init__(self, store=None):
        self.store = store
        self.tasks = {}
        if store:
            for task in store.list():
                self.tasks[task.id] = task

    def create(self, title):
        title = (title or "").strip()
        if not title:
            raise ValueError("task title cannot be empty")
        task = Task(title)
        self.tasks[task.id] = task
        if self.store:
            self.store.save(task)
        return task

    def set_status(self, id, status):
        if id not in self.tasks:
            raise KeyError(id)
        status = (status or "").strip().lower()
        if not status:
            raise ValueError("status cannot be empty")
        self.tasks[id].status = status
        if self.store:
            self.store.save(self.tasks[id])

    def list(self, status=None):
        items = list(self.tasks.values())
        if status is not None:
            items = [task for task in items if task.status == status]
        return items
