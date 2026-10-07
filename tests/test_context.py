from roster.context import ExecutionContext
def test_execution_context_child_merges_metadata():
    root=ExecutionContext("req-1",metadata={"source":"voice"}); child=root.child(tool="search")
    assert child.request_id==root.request_id and child.metadata=={"source":"voice","tool":"search"} and root.metadata=={"source":"voice"}
