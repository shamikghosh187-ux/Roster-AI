"""Translate model-produced workflow specifications into a validated task graph."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from roster.task_model import Task
from roster.task_planner import PlanningError, TaskPlanner


@dataclass(frozen=True)
class CognitiveTaskSpec:
    name: str
    input: str = ""
    depends_on: tuple[str, ...] = ()
    priority: int = 0
    metadata: dict[str, Any] | None = None


class CognitiveTaskGraph:
    """Validated graph representation owned by the cognitive core."""

    def __init__(self, specs: list[CognitiveTaskSpec]):
        self.specs = list(specs)
        self._tasks: dict[str, Task] = {}
        self.plan = self._build()

    def _build(self):
        tasks = []
        aliases = {}
        for index, spec in enumerate(self.specs):
            task = Task(
                name=spec.name,
                input=spec.input,
                priority=spec.priority,
                metadata=dict(spec.metadata or {}),
            )
            alias = str(index + 1)
            self._tasks[task.id] = task
            aliases[alias] = task.id
            tasks.append((task, ()))

        # Dependencies may refer to explicit task ids or 1-based spec indexes.
        normalized = []
        known = set()
        for index, spec in enumerate(self.specs):
            task = tasks[index][0]
            deps = []
            for dependency in spec.depends_on:
                dep_id = aliases.get(str(dependency), str(dependency))
                if dep_id not in self._tasks:
                    raise PlanningError(f"unknown cognitive dependency: {dependency}")
                deps.append(dep_id)
            normalized.append((task, tuple(deps)))
            known.add(task.id)

        return TaskPlanner().plan(normalized)

    def ready(self, completed: set[str] | None = None):
        completed = completed or set()
        return [
            step
            for step in self.plan.steps
            if step.task.id not in completed and set(step.depends_on) <= completed
        ]

    def task_by_name(self, name):
        for task in self._tasks.values():
            if task.name == name:
                return task
        return None
