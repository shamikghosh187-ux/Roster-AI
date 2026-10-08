class TaskObserver:
    def __init__(self): self.events=[]
    def on_event(self,event): self.events.append(event)
    def snapshot(self): return tuple(self.events)
