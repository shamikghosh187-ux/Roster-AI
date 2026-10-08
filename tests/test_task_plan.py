from roster.task_model import Task
from roster.task_plan import TaskPlan

def test_plan_preserves_dependency_edges():
    first=Task(name="first"); second=Task(name="second")
    plan=TaskPlan().add(first).add(second,[first.id])
    assert plan.ids()==(first.id,second.id)
    assert plan.steps[1].depends_on==(first.id,)
