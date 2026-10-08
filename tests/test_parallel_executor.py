from roster.parallel_executor import ParallelExecutor
from roster.task_model import Task
from roster.task_plan import PlanStep

def test_parallel_executor_returns_each_result():
    steps=[PlanStep(Task(name="a")),PlanStep(Task(name="b"))]
    results=ParallelExecutor(lambda step: step.task.name,max_workers=2).run(steps)
    assert sorted(results.values())==["a","b"]
