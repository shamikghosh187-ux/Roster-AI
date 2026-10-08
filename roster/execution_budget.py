"""Bounded execution budgets for tasks and workflows."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ExecutionBudget:
    max_tasks: int = 100
    max_tool_calls: int = 200
    max_failures: int = 20
    def __post_init__(self):
        if self.max_tasks < 1 or self.max_tool_calls < 1 or self.max_failures < 0:
            raise ValueError("execution budget values are invalid")

class BudgetExceeded(RuntimeError):
    pass

class BudgetTracker:
    def __init__(self,budget): self.budget=budget; self.tasks=0; self.tool_calls=0; self.failures=0
    def task_started(self):
        self.tasks += 1
        if self.tasks > self.budget.max_tasks: raise BudgetExceeded("task budget exceeded")
    def tool_started(self):
        self.tool_calls += 1
        if self.tool_calls > self.budget.max_tool_calls: raise BudgetExceeded("tool-call budget exceeded")
    def failure(self):
        self.failures += 1
        if self.failures > self.budget.max_failures: raise BudgetExceeded("failure budget exceeded")
