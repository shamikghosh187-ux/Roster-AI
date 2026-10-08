from roster.execution_trace import ExecutionTrace

def test_execution_trace_records_phases():
    trace=ExecutionTrace(); trace.record("t1","started"); trace.record("t1","completed")
    assert [r.phase for r in trace.records()]==["started","completed"]
