from roster.execution_event import ExecutionEvent

def test_execution_event_serializes_without_mutating_payload():
    event=ExecutionEvent("started","req","task",{"attempt":1})
    assert event.as_dict()["kind"] == "started"
    assert event.as_dict()["payload"]["attempt"] == 1
