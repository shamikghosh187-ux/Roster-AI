from roster.cancel import CancelledError
from roster.execution_trace import ExecutionTrace
from roster.task_cancellation import check_cancelled
from roster.task_plan import TaskPlan
from roster.task_priority import prioritize

class TaskOrchestrator:
    def __init__(self,execute):
        self.execute=execute
        self.trace=ExecutionTrace()

    def run(self,plan: TaskPlan,cancellation=None):
        completed=set(); results={}; pending=list(plan.steps)
        while pending:
            selected=None
            try:
                check_cancelled(cancellation)
                ready=[step for step in pending if set(step.depends_on)<=completed]
                if not ready: raise RuntimeError("plan cannot make progress")
                task=prioritize([item.task for item in ready])[0]
                selected=next(item for item in ready if item.task.id==task.id)
                self.trace.record(selected.task.id,"started")
                result=self.execute(selected)
                if hasattr(result,"ok") and not result.ok:
                    detail=result.error or "task execution failed"
                    raise RuntimeError(detail)
                results[selected.task.id]=result
                completed.add(selected.task.id)
                pending.remove(selected)
                self.trace.record(selected.task.id,"completed")
            except CancelledError:
                self.trace.record(selected.task.id if selected else "plan","cancelled")
                raise
            except Exception as exc:
                self.trace.record(selected.task.id if selected else "plan","failed",str(exc))
                raise
        return results
