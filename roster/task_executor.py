from roster.cancel import CancelledError
from roster.task_events import make_task_event
from roster.task_model import TaskStatus
from roster.task_state import TaskStateStore
from roster.tool_invocation import ToolInvocation

class TaskExecutor:
    def __init__(self,tool_executor,state=None):
        self.tool_executor=tool_executor
        self.state=state or TaskStateStore()
        self.events=[]

    def execute(self,task,tool_name,arguments,request_id=""):
        if self.state.get(task.id) is None:
            self.state.add(task)
        current=self.state.get(task.id).status
        if current == TaskStatus.PENDING:
            self.state.move(task.id,TaskStatus.PLANNING)
            self.state.move(task.id,TaskStatus.READY)
            self.state.move(task.id,TaskStatus.RUNNING)
        elif current == TaskStatus.READY:
            self.state.move(task.id,TaskStatus.RUNNING)
        elif current != TaskStatus.RUNNING:
            raise RuntimeError(f"task is not executable from state: {current.value}")

        self.events.append(make_task_event(task.id,"started",tool=tool_name))
        invocation=ToolInvocation(tool_name,arguments,task.id,request_id).normalized()
        try:
            if hasattr(self.tool_executor,"execute_request"):
                result=self.tool_executor.execute_request(invocation)
            else:
                result=self.tool_executor.execute(invocation.tool_name,invocation.arguments,task.id)
        except CancelledError:
            self.state.move(task.id,TaskStatus.CANCELLED)
            self.events.append(make_task_event(task.id,"cancelled"))
            raise
        except Exception as exc:
            self.state.move(task.id,TaskStatus.FAILED)
            self.events.append(make_task_event(task.id,"failed",error=str(exc)))
            raise

        if result.ok:
            self.state.move(task.id,TaskStatus.COMPLETED)
            self.events.append(make_task_event(task.id,"completed"))
        else:
            self.state.move(task.id,TaskStatus.FAILED)
            self.events.append(make_task_event(task.id,"failed",error=result.error))
        return result
