"""Resolve execution policy from explicit settings with safe defaults."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ResolvedExecutionPolicy:
    timeout_seconds:float=30.0
    max_retries:int=0
    confirmation_required:bool=True
    max_parallel_tasks:int=1
    def __post_init__(self):
        if self.timeout_seconds<=0: raise ValueError("timeout_seconds must be positive")
        if self.max_retries<0: raise ValueError("max_retries cannot be negative")
        if self.max_parallel_tasks<1: raise ValueError("max_parallel_tasks must be positive")

def resolve_execution_policy(settings)->ResolvedExecutionPolicy:
    get=settings.get if settings is not None else lambda key,default=None: default
    return ResolvedExecutionPolicy(
        timeout_seconds=float(get("assistant.tool_timeout_seconds",30.0)),
        max_retries=int(get("performance.max_retries",0)),
        confirmation_required=get("assistant.confirmation","smart")!="never",
        max_parallel_tasks=int(get("assistant.max_parallel_tasks",1)),
    )
