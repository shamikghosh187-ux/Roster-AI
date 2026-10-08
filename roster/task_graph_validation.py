"""Validation for dependency graphs before execution starts."""
from __future__ import annotations
from typing import Iterable

class TaskGraphError(ValueError):
    pass

def validate_dependencies(tasks: Iterable[object]) -> None:
    items = list(tasks)
    ids = {getattr(t, "id", None) for t in items}
    if None in ids:
        raise TaskGraphError("every task must have an id")
    for task in items:
        deps = tuple(getattr(task, "depends_on", ()) or ())
        missing = [dep for dep in deps if dep not in ids]
        if missing:
            raise TaskGraphError(f"task {task.id} has missing dependencies: {missing}")
    graph = {task.id: set(getattr(task, "depends_on", ()) or ()) for task in items}
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str) -> None:
        if node in visiting:
            raise TaskGraphError("task dependency cycle detected")
        if node in visited:
            return
        visiting.add(node)
        for dep in graph[node]:
            visit(dep)
        visiting.remove(node)
        visited.add(node)
    for node in graph:
        visit(node)
