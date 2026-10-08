import pytest
from roster.execution_budget import BudgetExceeded,BudgetTracker,ExecutionBudget

def test_budget_counter_does_not_overshoot_on_rejection():
    tracker=BudgetTracker(ExecutionBudget(max_tasks=1,max_tool_calls=1,max_failures=1))
    assert tracker.task_started()==1
    with pytest.raises(BudgetExceeded): tracker.task_started()
    assert tracker.tasks==1
    assert tracker.tool_started()==1
    with pytest.raises(BudgetExceeded): tracker.tool_started()
    assert tracker.tool_calls==1
    assert tracker.failure()==1
    with pytest.raises(BudgetExceeded): tracker.failure()
    assert tracker.failures==1
