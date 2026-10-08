from roster.task_model import Task
from roster.task_queue import TaskQueue

def test_queue_pops_highest_priority():
    queue=TaskQueue(); queue.push(Task(name="low",priority=1)); queue.push(Task(name="high",priority=5))
    assert queue.pop_ready().name=="high"
