"""Thread-safe bounded execution budgets for tasks and workflows."""
from __future__ import annotations
from dataclasses import dataclass
from threading import Lock

@dataclass(frozen=True)
class ExecutionBudget:
    max_tasks:int=100
    max_tool_calls:int=200
    max_failures:int=20
    def __post_init__(self):
        if self.max_tasks<1 or self.max_tool_calls<1 or self.max_failures<0:
            raise ValueError("execution budget values are invalid")

class BudgetExceeded(RuntimeError): pass

class BudgetTracker:
    def __init__(self,budget):
        self.budget=budget
        self.tasks=0
        self.tool_calls=0
        self.failures=0
        self._lock=Lock()

    def _reserve(self,current,limit,message):
        if current>=limit: raise BudgetExceeded(message)
        return current+1

    def task_started(self):
        with self._lock:
            self.tasks=self._reserve(self.tasks,self.budget.max_tasks,"task budget exceeded")
            return self.tasks

    def tool_started(self):
        with self._lock:
            self.tool_calls=self._reserve(self.tool_calls,self.budget.max_tool_calls,"tool-call budget exceeded")
            return self.tool_calls

    def failure(self):
        with self._lock:
            self.failures=self._reserve(self.failures,self.budget.max_failures,"failure budget exceeded")
            return self.failures
