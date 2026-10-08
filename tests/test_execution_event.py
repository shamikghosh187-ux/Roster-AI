from roster.execution_event import ExecutionEvent

def test_execution_event_serializes_without_mutating_payload():
    event=ExecutionEvent("started","req","task",{"attempt":1})
    assert event.as_dict()["kind"] == "started"
    assert event.as_dict()["payload"]["attempt"] == 1


def test_event_payload_isolated_from_input():
    payload={"attempt":1}
    event=ExecutionEvent("started","req",payload=payload)
    payload["attempt"]=2
    assert event.payload["attempt"]==1

def test_event_rejects_empty_identity():
    import pytest
    with pytest.raises(ValueError): ExecutionEvent("", "req")
    with pytest.raises(ValueError): ExecutionEvent("started", "")
