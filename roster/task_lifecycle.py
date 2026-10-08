from roster.task_model import TaskStatus

_ALLOWED={
 TaskStatus.PENDING:{TaskStatus.PLANNING,TaskStatus.CANCELLED},
 TaskStatus.PLANNING:{TaskStatus.READY,TaskStatus.FAILED,TaskStatus.CANCELLED},
 TaskStatus.READY:{TaskStatus.RUNNING,TaskStatus.CANCELLED},
 TaskStatus.RUNNING:{TaskStatus.WAITING,TaskStatus.COMPLETED,TaskStatus.FAILED,TaskStatus.CANCELLED},
 TaskStatus.WAITING:{TaskStatus.RUNNING,TaskStatus.FAILED,TaskStatus.CANCELLED},
 TaskStatus.COMPLETED:set(),TaskStatus.FAILED:set(),TaskStatus.CANCELLED:set(),
}
class InvalidTaskTransition(RuntimeError): pass

def can_transition(current,target): return target in _ALLOWED[current]

def transition(current,target):
    if not can_transition(current,target): raise InvalidTaskTransition(f"cannot transition {current.value} -> {target.value}")
    return target
