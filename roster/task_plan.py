from dataclasses import dataclass, field
from roster.task_model import Task
from roster.task_dependencies import DependencyGraph

@dataclass(frozen=True)
class PlanStep:
    task: Task
    depends_on: tuple[str,...]=field(default_factory=tuple)

@dataclass
class TaskPlan:
    steps: list[PlanStep]=field(default_factory=list)
    def add(self,task,depends_on=()):
        graph=DependencyGraph()
        for step in self.steps: graph.add(step.task.id,step.depends_on)
        graph.add(task.id,depends_on)
        self.steps.append(PlanStep(task,tuple(depends_on)))
        return self
    def ids(self): return tuple(step.task.id for step in self.steps)
