from enum import Enum

class AgentState(str,Enum):
    IDLE="idle"
    PLANNING="planning"
    WAITING_PERMISSION="waiting_permission"
    EXECUTING="executing"
    OBSERVING="observing"
    COMPLETED="completed"
    FAILED="failed"
    CANCELLED="cancelled"

_ALLOWED={
    AgentState.IDLE:{AgentState.PLANNING,AgentState.EXECUTING},
    AgentState.PLANNING:{AgentState.WAITING_PERMISSION,AgentState.EXECUTING,AgentState.COMPLETED,AgentState.FAILED,AgentState.CANCELLED},
    AgentState.WAITING_PERMISSION:{AgentState.EXECUTING,AgentState.COMPLETED,AgentState.FAILED,AgentState.CANCELLED},
    AgentState.EXECUTING:{AgentState.OBSERVING,AgentState.COMPLETED,AgentState.FAILED,AgentState.CANCELLED},
    AgentState.OBSERVING:{AgentState.PLANNING,AgentState.COMPLETED,AgentState.FAILED,AgentState.CANCELLED},
    AgentState.COMPLETED:set(),
    AgentState.FAILED:set(),
    AgentState.CANCELLED:set(),
}

class InvalidStateTransition(RuntimeError): pass

class StateMachine:
    def __init__(self): self.state=AgentState.IDLE
    def move(self,state):
        target=AgentState(state)
        if target is self.state:return self.state
        if target not in _ALLOWED[self.state]:
            raise InvalidStateTransition(f"cannot transition {self.state.value} -> {target.value}")
        self.state=target
        return self.state
    def reset(self):
        if self.state in {AgentState.COMPLETED,AgentState.FAILED,AgentState.CANCELLED}:
            self.state=AgentState.IDLE
        return self.state
