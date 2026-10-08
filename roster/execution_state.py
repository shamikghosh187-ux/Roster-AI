"""Explicit lifecycle states for production task execution."""
from enum import Enum

class ExecutionState(str,Enum):
    PENDING="pending"
    RUNNING="running"
    WAITING="waiting"
    COMPLETED="completed"
    FAILED="failed"
    CANCELLED="cancelled"

_TERMINAL={ExecutionState.COMPLETED,ExecutionState.FAILED,ExecutionState.CANCELLED}

def is_terminal(state): return ExecutionState(state) in _TERMINAL

def can_transition(source,target):
    source,target=ExecutionState(source),ExecutionState(target)
    if source in _TERMINAL: return False
    if source==ExecutionState.PENDING: return target in {ExecutionState.RUNNING,ExecutionState.CANCELLED}
    if source==ExecutionState.RUNNING: return target in {ExecutionState.WAITING,ExecutionState.COMPLETED,ExecutionState.FAILED,ExecutionState.CANCELLED}
    if source==ExecutionState.WAITING: return target in {ExecutionState.RUNNING,ExecutionState.FAILED,ExecutionState.CANCELLED}
    return False
