from roster.events import EventBus

def test_runtime_event_deep_copies_nested_payloads():
    bus=EventBus()
    nested={"meta":{"source":"user"}}
    event=bus.emit("done",payload=nested)
    event.payload["payload"]["meta"]["source"]="mutated"
    assert nested["meta"]["source"]=="user"

def test_runtime_event_rejects_non_mapping_payload():
    try:
        from roster.events import RuntimeEvent
        RuntimeEvent("done",payload=["not","a","dict"])
    except TypeError:
        return
    raise AssertionError("expected TypeError")
