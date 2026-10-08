import pytest
from roster.execution_session import ExecutionSession
from roster.execution_state import ExecutionState

def test_session_tracks_state_and_results():
    session=ExecutionSession("req")
    session.transition(ExecutionState.RUNNING)
    session.record_result("t1", "ok")
    session.transition(ExecutionState.COMPLETED)
    assert session.state is ExecutionState.COMPLETED
    assert session.task_results == {"t1":"ok"}

def test_session_rejects_invalid_transition():
    with pytest.raises(ValueError): ExecutionSession("req").transition(ExecutionState.COMPLETED)


def test_session_rejects_empty_request_id():
    import pytest
    with pytest.raises(ValueError): ExecutionSession("")

def test_session_snapshot_isolated_from_internal_state():
    session=ExecutionSession("req")
    session.record_result("t1","ok")
    state,results,metadata=session.snapshot()
    results["t2"]="bad"; metadata["x"]=1
    assert "t2" not in session.task_results
    assert "x" not in session.metadata
