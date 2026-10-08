from roster.execution_state import ExecutionState,can_transition,is_terminal

def test_running_can_complete_or_fail():
    assert can_transition(ExecutionState.RUNNING,ExecutionState.COMPLETED)
    assert can_transition(ExecutionState.RUNNING,ExecutionState.FAILED)

def test_terminal_states_cannot_transition():
    assert is_terminal(ExecutionState.COMPLETED)
    assert not can_transition(ExecutionState.COMPLETED,ExecutionState.RUNNING)
