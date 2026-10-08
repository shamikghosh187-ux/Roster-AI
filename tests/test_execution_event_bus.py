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


def test_event_bus_can_unsubscribe_and_avoid_duplicate_registration():
    seen=[]
    def callback(event): seen.append(event)
    bus=ExecutionEventBus()
    bus.subscribe(callback); bus.subscribe(callback)
    assert bus.subscriber_count()==1
    event=ExecutionEvent("started","r")
    bus.publish(event)
    assert seen==[event]
    assert bus.unsubscribe(callback) is True
    assert bus.unsubscribe(callback) is False
    assert bus.subscriber_count()==0
