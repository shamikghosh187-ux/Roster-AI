from dataclasses import dataclass, field
from roster.task_graph_validation import validate_dependencies
from roster.task_model import Task

@dataclass(frozen=True)
class PlanStep:
    task: Task
    depends_on: tuple[str,...]=field(default_factory=tuple)

@dataclass
class TaskPlan:
    steps: list[PlanStep]=field(default_factory=list)
    def add(self,task,depends_on=()):
        candidate=PlanStep(task,tuple(depends_on))
        validate_dependencies([*self.steps,candidate])
        self.steps.append(candidate)
        return self
    def validate(self):
        validate_dependencies(self.steps)
        return self
    def ids(self): return tuple(step.task.id for step in self.steps)
