from roster.task_model import Task
from roster.task_orchestrator import TaskOrchestrator
from roster.task_plan import TaskPlan

def test_orchestrator_executes_dependency_order():
    a=Task(name="a"); b=Task(name="b")
    plan=TaskPlan().add(a).add(b,[a.id]); order=[]
    result=TaskOrchestrator(lambda step: order.append(step.task.name) or step.task.name).run(plan)
    assert order==["a","b"]
    assert result[b.id]=="b"
