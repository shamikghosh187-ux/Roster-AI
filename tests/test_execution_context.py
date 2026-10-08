from roster.execution_context import ExecutionContext

def test_context_child_is_immutable_from_parent():
    root = ExecutionContext("req", "session", {"source": "voice"})
    child = root.child(tool="search")
    assert root.metadata == {"source": "voice"}
    assert child.metadata == {"source": "voice", "tool": "search"}
    assert child.request_id == root.request_id


def test_context_rejects_empty_request_id():
    import pytest
    with pytest.raises(ValueError): ExecutionContext("")

def test_context_metadata_isolated_from_input():
    metadata={"source":"voice"}
    context=ExecutionContext("req",metadata=metadata)
    metadata["source"]="changed"
    assert context.metadata["source"]=="voice"
