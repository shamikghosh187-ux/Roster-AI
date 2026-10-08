"""Stateful execution session shared by orchestration components."""
from __future__ import annotations
from dataclasses import dataclass,field
from threading import RLock
from roster.execution_state import ExecutionState,can_transition

@dataclass
class ExecutionSession:
    request_id:str
    state:ExecutionState=ExecutionState.PENDING
    task_results:dict[str,object]=field(default_factory=dict)
    metadata:dict[str,object]=field(default_factory=dict)

    def __post_init__(self):
        if not self.request_id or not self.request_id.strip():
            raise ValueError("request_id cannot be empty")
        self.task_results=dict(self.task_results)
        self.metadata=dict(self.metadata)
        self._lock=RLock()

    def transition(self,target):
        target=ExecutionState(target)
        with self._lock:
            if not can_transition(self.state,target):
                raise ValueError(f"invalid execution transition: {self.state.value} -> {target.value}")
            self.state=target
            return self.state

    def record_result(self,task_id,result):
        if not task_id or not str(task_id).strip(): raise ValueError("task_id cannot be empty")
        with self._lock:
            self.task_results[task_id]=result

    def snapshot(self):
        with self._lock:
            return self.state,dict(self.task_results),dict(self.metadata)
