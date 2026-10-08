from roster.execution_context import ExecutionContext

def test_context_child_is_immutable_from_parent():
    root = ExecutionContext("req", "session", {"source": "voice"})
    child = root.child(tool="search")
    assert root.metadata == {"source": "voice"}
    assert child.metadata == {"source": "voice", "tool": "search"}
    assert child.request_id == root.request_id
