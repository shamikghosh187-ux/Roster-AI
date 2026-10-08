"""Stateful execution session shared by orchestration components."""
from __future__ import annotations
from dataclasses import dataclass,field
from roster.execution_state import ExecutionState,can_transition

@dataclass
class ExecutionSession:
    request_id: str
    state: ExecutionState = ExecutionState.PENDING
    task_results: dict[str,object] = field(default_factory=dict)
    metadata: dict[str,object] = field(default_factory=dict)
    def transition(self,target):
        target=ExecutionState(target)
        if not can_transition(self.state,target):
            raise ValueError(f"invalid execution transition: {self.state.value} -> {target.value}")
        self.state=target
        return self.state
    def record_result(self,task_id,result): self.task_results[task_id]=result
