from roster.task_model import Task
from roster.task_plan import TaskPlan

class PlanningError(ValueError): pass

class TaskPlanner:
    """Builds a validated plan from task specifications without executing them."""
    def plan(self, tasks):
        plan=TaskPlan()
        known=set()
        for task,dependencies in tasks:
            dependencies=tuple(dependencies)
            missing=set(dependencies)-known
            if missing: raise PlanningError(f"unknown task dependencies: {sorted(missing)}")
            plan.add(task,dependencies)
            known.add(task.id)
        return plan
