from roster.task_model import Task
from roster.task_plan import PlanStep
from roster.sequential_executor import SequentialExecutor

def test_sequential_executor_respects_dependencies():
    a=Task(name="a"); b=Task(name="b"); order=[]
    steps=[PlanStep(a),PlanStep(b,(a.id,))]
    results=SequentialExecutor(lambda step: order.append(step.task.name) or step.task.name).run(steps)
    assert order==["a","b"]
    assert results[b.id]=="b"
