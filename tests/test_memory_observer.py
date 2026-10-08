from roster.memory_events import MemoryEvent
from roster.memory_observer import MemoryObserver

def test_observer_notifies_subscribers():
    seen=[]; observer=MemoryObserver(); observer.subscribe(seen.append); observer.emit(MemoryEvent("created","x")); assert seen[0].key=="x"
