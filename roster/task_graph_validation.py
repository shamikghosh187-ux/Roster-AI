"""Validation for dependency graphs before execution starts."""
from __future__ import annotations
from typing import Iterable

class TaskGraphError(ValueError): pass

def _identity(item):
    task=getattr(item,"task",None)
    if task is not None:
        return getattr(task,"id",None), tuple(getattr(item,"depends_on",()) or ())
    return getattr(item,"id",None), tuple(getattr(item,"depends_on",()) or ())

def validate_dependencies(tasks:Iterable[object])->None:
    items=list(tasks)
    identities=[_identity(item) for item in items]
    ids=[item_id for item_id,_ in identities]
    if any(not item_id for item_id in ids):
        raise TaskGraphError("every task must have an id")
    if len(ids)!=len(set(ids)):
        raise TaskGraphError("task dependency graph contains duplicate task ids")
    known=set(ids)
    for item,(item_id,deps) in zip(items,identities):
        missing=[dep for dep in deps if dep not in known]
        if missing:
            raise TaskGraphError(f"task {item_id} has missing dependencies: {missing}")
    graph={item_id:set(deps) for item_id,deps in identities}
    visiting=set(); visited=set()
    def visit(node):
        if node in visiting: raise TaskGraphError("task dependency cycle detected")
        if node in visited:return
        visiting.add(node)
        for dep in graph[node]:visit(dep)
        visiting.remove(node); visited.add(node)
    for node in graph:visit(node)
