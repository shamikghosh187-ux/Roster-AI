import pytest
from roster.execution_budget import BudgetExceeded,BudgetTracker,ExecutionBudget

def test_task_budget_is_enforced():
    tracker=BudgetTracker(ExecutionBudget(max_tasks=1))
    tracker.task_started()
    with pytest.raises(BudgetExceeded): tracker.task_started()

def test_failure_budget_is_enforced():
    tracker=BudgetTracker(ExecutionBudget(max_failures=1))
    tracker.failure()
    with pytest.raises(BudgetExceeded): tracker.failure()
