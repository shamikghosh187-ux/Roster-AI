from roster.execution_event import ExecutionEvent
from roster.execution_event_bus import ExecutionEventBus

def test_event_bus_notifies_subscribers():
    seen=[]; bus=ExecutionEventBus(); bus.subscribe(seen.append)
    event=ExecutionEvent("started","r","t")
    assert bus.publish(event) == ()
    assert seen == [event]

def test_event_bus_isolates_subscriber_failures():
    bus=ExecutionEventBus(); bus.subscribe(lambda _: (_ for _ in ()).throw(RuntimeError("bad")))
    assert len(bus.publish(ExecutionEvent("x","r"))) == 1
