from roster.task_events import make_task_event

def test_task_event_contains_identity_and_payload():
    event=make_task_event("abc","started",attempt=1)
    assert event.task_id=="abc"
    assert event.name=="started"
    assert event.payload=={"attempt":1}
    assert event.created_at
