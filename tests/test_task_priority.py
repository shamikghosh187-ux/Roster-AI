from roster.task_model import Task
from roster.task_priority import prioritize

def test_priority_orders_high_first():
    low=Task(name="low",priority=1); high=Task(name="high",priority=9)
    assert prioritize([low,high])[0].name=="high"
