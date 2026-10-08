from roster.memory_events import MemoryEvent

def test_memory_event_is_immutable_domain_data():
    event=MemoryEvent("created","city"); assert event.type=="created"
