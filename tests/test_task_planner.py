import pytest
from roster.task_model import Task
from roster.task_planner import PlanningError, TaskPlanner

def test_planner_rejects_unknown_dependency():
    task=Task(name="work")
    with pytest.raises(PlanningError): TaskPlanner().plan([(task,("missing",))])

def test_planner_builds_ordered_plan():
    a=Task(name="a"); b=Task(name="b")
    plan=TaskPlanner().plan([(a,()),(b,(a.id,))])
    assert [s.task.name for s in plan.steps]==["a","b"]
