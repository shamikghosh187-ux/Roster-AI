from roster.task_model import Task
from roster.task_orchestrator import TaskOrchestrator
from roster.task_plan import TaskPlan

class OrchestrationService:
    def __init__(self,execute): self._execute=execute
    def run_tasks(self,tasks,cancellation=None):
        plan=TaskPlan()
        for task,deps in tasks: plan.add(task,deps)
        return TaskOrchestrator(self._execute).run(plan,cancellation)
