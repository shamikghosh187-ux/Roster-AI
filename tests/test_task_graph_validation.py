import pytest
from roster.task_graph_validation import TaskGraphError, validate_dependencies

class T:
    def __init__(self, id, depends_on=()):
        self.id=id; self.depends_on=depends_on

def test_dependency_graph_accepts_dag():
    validate_dependencies([T("a"), T("b", ("a",)), T("c", ("a", "b"))])

def test_dependency_graph_rejects_missing_dependency():
    with pytest.raises(TaskGraphError):
        validate_dependencies([T("a", ("missing",))])

def test_dependency_graph_rejects_cycle():
    with pytest.raises(TaskGraphError):
        validate_dependencies([T("a", ("b",)), T("b", ("a",))])
