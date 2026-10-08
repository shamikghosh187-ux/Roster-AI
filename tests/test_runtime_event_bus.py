import pytest
from roster.events import EventBus

def test_runtime_event_bus_deduplicates_and_unsubscribes():
    bus=EventBus(); seen=[]
    callback=seen.append
    bus.subscribe("done",callback); bus.subscribe("done",callback)
    event=bus.emit("done",value=1)
    assert seen==[event]
    assert bus.unsubscribe("done",callback) is True
    assert bus.unsubscribe("done",callback) is False

def test_runtime_event_payload_isolated():
    bus=EventBus(); event=bus.emit("done",value=1)
    event.payload["value"]=2
    assert event.payload["value"]==2
    with pytest.raises(ValueError): bus.subscribe("",lambda _:None)
