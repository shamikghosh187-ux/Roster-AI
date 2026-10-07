from dataclasses import dataclass
from datetime import datetime,timezone,timedelta
@dataclass
class Schedule: task_id:str; run_at:datetime; repeat_seconds:int|None=None
class Scheduler:
    def __init__(self): self.items=[]
    def schedule(self,task_id,delay_seconds,repeat_seconds=None):
        x=Schedule(task_id,datetime.now(timezone.utc)+timedelta(seconds=max(0,delay_seconds)),repeat_seconds); self.items.append(x); return x
    def due(self,now=None): return [x for x in self.items if x.run_at <= (now or datetime.now(timezone.utc))]
