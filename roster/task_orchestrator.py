from roster.execution_trace import ExecutionTrace
from roster.task_cancellation import check_cancelled
from roster.task_plan import TaskPlan
from roster.task_priority import prioritize

class TaskOrchestrator:
    def __init__(self,execute): self.execute=execute; self.trace=ExecutionTrace()
    def run(self,plan: TaskPlan, cancellation=None):
        completed=set(); results={}
        pending=list(plan.steps)
        while pending:
            check_cancelled(cancellation)
            ready=[step for step in pending if set(step.depends_on)<=completed]
            if not ready: raise RuntimeError("plan cannot make progress")
            step=prioritize([item.task for item in ready])[0]
            selected=next(item for item in ready if item.task.id==step.id)
            self.trace.record(step.id,"started")
            results[step.id]=self.execute(selected)
            completed.add(step.id); pending.remove(selected)
            self.trace.record(step.id,"completed")
        return results
