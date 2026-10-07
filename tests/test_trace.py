from roster.trace import ExecutionTrace

def test_trace_records_ordered_events():
    trace = ExecutionTrace()
    trace.record("request_started", user_text="hello")
    trace.record("planning", step=1)
    trace.record("tool_finished", result="done")
    events = trace.as_dicts()
    assert [e["event"] for e in events] == ["request_started", "planning", "tool_finished"]
    assert events[1]["data"]["step"] == 1
