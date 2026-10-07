from dataclasses import dataclass,field
import uuid
@dataclass
class Task:
    title:str
    status:str='pending'
    id:str=field(default_factory=lambda:uuid.uuid4().hex)
class TaskEngine:
    def __init__(self): self.tasks={}
    def create(self,title): t=Task(title); self.tasks[t.id]=t; return t
    def set_status(self,id,status): self.tasks[id].status=status
    def list(self): return list(self.tasks.values())
