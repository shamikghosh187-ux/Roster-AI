from collections import deque
from roster.task_priority import prioritize

class TaskQueue:
    def __init__(self): self._items=[]
    def push(self,task): self._items.append(task)
    def extend(self,tasks): self._items.extend(tasks)
    def pop_ready(self,completed=()):
        done=set(completed)
        ready=[task for task in self._items if task.id not in done]
        if not ready: return None
        selected=prioritize(ready)[0]
        self._items.remove(selected)
        return selected
    def __len__(self): return len(self._items)
