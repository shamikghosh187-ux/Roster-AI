"""Single gateway combining policy, repository, ranking and observation."""
from roster.memory_record import MemoryRecord
from roster.memory_query import MemoryQuery
from roster.memory_ranker import rank
from roster.memory_events import MemoryEvent

class MemoryGateway:
    def __init__(self,repository,observer=None): self.repository=repository; self.observer=observer
    def remember(self,record):
        accepted=self.repository.save(record)
        if accepted and self.observer: self.observer.emit(MemoryEvent("created",record.key,record.source))
        return accepted
    def recall(self,query): return rank(self.repository.all(),query)
