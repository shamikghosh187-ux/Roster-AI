from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ToolResult:
    ok: bool
    value: Any = None
    error: str | None = None
    retryable: bool = False
    @classmethod
    def success(cls,value=None): return cls(True,value)
    @classmethod
    def failure(cls,error,retryable=False): return cls(False,None,error,retryable)
