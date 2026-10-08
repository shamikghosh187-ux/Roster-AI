"""Structured long-term memory records."""
from copy import deepcopy
from dataclasses import dataclass,field
from datetime import datetime,timezone
from typing import Any

@dataclass(frozen=True)
class MemoryRecord:
    key:str
    value:str
    kind:str="fact"
    confidence:float=1.0
    importance:float=0.5
    source:str="conversation"
    created_at:str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())
    metadata:dict[str,Any]=field(default_factory=dict)
    def __post_init__(self):
        if not isinstance(self.key,str) or not self.key.strip(): raise ValueError("memory key cannot be empty")
        if not isinstance(self.value,str): raise TypeError("memory value must be a string")
        if not isinstance(self.kind,str) or not self.kind.strip(): raise ValueError("memory kind cannot be empty")
        if not isinstance(self.source,str) or not self.source.strip(): raise ValueError("memory source cannot be empty")
        if not 0<=self.confidence<=1: raise ValueError("confidence must be between 0 and 1")
        if not 0<=self.importance<=1: raise ValueError("importance must be between 0 and 1")
        object.__setattr__(self,"metadata",deepcopy(self.metadata))
    @property
    def score(self)->float: return self.confidence*self.importance
