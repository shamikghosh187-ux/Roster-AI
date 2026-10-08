from roster.models import Action
from roster.orchestration import OrchestrationService
from roster.task_model import Task

def test_orchestration_service_runs_tasks():
    a=Task(name="a"); b=Task(name="b")
    service=OrchestrationService(lambda step: step.task.name)
    result=service.run_tasks([(a,()),(b,(a.id,))])
    assert result[a.id]=="a" and result[b.id]=="b"
