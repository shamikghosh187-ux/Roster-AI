"""Explicit operation result type for tool and integration boundaries."""
from dataclasses import dataclass
from typing import Generic,TypeVar
T=TypeVar("T")
@dataclass(frozen=True)
class OperationResult(Generic[T]):
    ok:bool
    value:T|None=None
    error:str|None=None
    @classmethod
    def success(cls,value=None): return cls(True,value,None)
    @classmethod
    def failure(cls,error:str):
        if not error: raise ValueError("error cannot be empty")
        return cls(False,None,error)
