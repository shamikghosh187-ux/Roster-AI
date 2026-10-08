"""Request-scoped execution context without coupling to the UI."""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Any

@dataclass(frozen=True)
class ExecutionContext:
    request_id:str
    session_id:str|None=None
    metadata:dict[str,Any]=field(default_factory=dict)

    def __post_init__(self):
        if not self.request_id or not self.request_id.strip():
            raise ValueError("request_id cannot be empty")
        object.__setattr__(self,"metadata",dict(self.metadata))

    def child(self,**metadata:Any)->"ExecutionContext":
        merged=dict(self.metadata)
        merged.update(metadata)
        return ExecutionContext(self.request_id,self.session_id,merged)
