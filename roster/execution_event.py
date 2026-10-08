"""Typed execution events for observability adapters."""
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ExecutionEvent:
    kind:str
    request_id:str
    task_id:str|None=None
    payload:dict[str,Any]|None=None
    def __post_init__(self):
        if not self.kind or not self.kind.strip(): raise ValueError("event kind cannot be empty")
        if not self.request_id or not self.request_id.strip(): raise ValueError("request_id cannot be empty")
        object.__setattr__(self,"payload",deepcopy(self.payload or {}))
    def as_dict(self):
        return {"kind":self.kind,"request_id":self.request_id,"task_id":self.task_id,"payload":deepcopy(self.payload or {})}
