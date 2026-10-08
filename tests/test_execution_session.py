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
