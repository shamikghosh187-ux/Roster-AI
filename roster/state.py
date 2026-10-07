from enum import Enum

class AgentState(str, Enum):
    IDLE='idle'
    PLANNING='planning'
    WAITING_PERMISSION='waiting_permission'
    EXECUTING='executing'
    OBSERVING='observing'
    COMPLETED='completed'
    FAILED='failed'
    CANCELLED='cancelled'

class StateMachine:
    def __init__(self): self.state=AgentState.IDLE
    def move(self,state): self.state=AgentState(state); return self.state
