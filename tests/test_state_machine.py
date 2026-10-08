import pytest
from roster.state import AgentState, InvalidStateTransition, StateMachine

def test_state_machine_enforces_normal_request_lifecycle():
    machine=StateMachine()
    machine.move(AgentState.PLANNING)
    machine.move(AgentState.EXECUTING)
    machine.move(AgentState.OBSERVING)
    machine.move(AgentState.PLANNING)
    machine.move(AgentState.COMPLETED)
    assert machine.state is AgentState.COMPLETED

def test_state_machine_rejects_invalid_transition():
    machine=StateMachine()
    with pytest.raises(InvalidStateTransition):
        machine.move(AgentState.COMPLETED)

def test_state_machine_can_reset_after_terminal_request():
    machine=StateMachine()
    machine.move(AgentState.PLANNING); machine.move(AgentState.EXECUTING); machine.move(AgentState.COMPLETED)
    assert machine.reset() is AgentState.IDLE
