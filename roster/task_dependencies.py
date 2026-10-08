from dataclasses import dataclass, field

@dataclass(frozen=True)
class TaskDependency:
    task_id: str
    depends_on: tuple[str,...]=field(default_factory=tuple)

class DependencyError(ValueError): pass

class DependencyGraph:
    def __init__(self): self._edges: dict[str,set[str]]={}
    def add(self,task_id,depends_on=()):
        deps=set(depends_on)
        if task_id in deps: raise DependencyError("a task cannot depend on itself")
        self._edges.setdefault(task_id,set()).update(deps)
        if self.has_cycle():
            for dep in deps: self._edges[task_id].discard(dep)
            raise DependencyError("task dependency cycle detected")
    def dependencies(self,task_id): return frozenset(self._edges.get(task_id,set()))
    def ready(self,completed):
        done=set(completed)
        return tuple(sorted(k for k,v in self._edges.items() if k not in done and v <= done))
    def has_cycle(self):
        visiting=set(); visited=set()
        def visit(node):
            if node in visiting: return True
            if node in visited: return False
            visiting.add(node)
            if any(visit(dep) for dep in self._edges.get(node,set())): return True
            visiting.remove(node); visited.add(node); return False
        return any(visit(node) for node in self._edges)
