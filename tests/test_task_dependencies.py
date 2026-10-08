import pytest
from roster.task_dependencies import DependencyError, DependencyGraph

def test_ready_tasks_require_dependencies():
    graph=DependencyGraph(); graph.add("b",["a"]); graph.add("a")
    assert graph.ready(set())==("a",)
    assert graph.ready({"a"})==("b",)

def test_cycles_are_rejected():
    graph=DependencyGraph(); graph.add("a")
    graph.add("b",["a"])
    with pytest.raises(DependencyError): graph.add("a",["b"])
