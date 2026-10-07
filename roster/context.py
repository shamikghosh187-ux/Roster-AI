"""Execution context propagation for request metadata."""
from dataclasses import dataclass,field
from typing import Any
@dataclass
class ExecutionContext:
    request_id:str
    user:str="local"
    metadata:dict[str,Any]=field(default_factory=dict)
    def child(self,**metadata:Any):
        merged=dict(self.metadata); merged.update(metadata)
        return ExecutionContext(self.request_id,self.user,merged)
