from roster.task_observer import TaskObserver

def test_task_observer_captures_events():
    observer=TaskObserver(); observer.on_event("started"); observer.on_event("completed")
    assert observer.snapshot()==("started","completed")
