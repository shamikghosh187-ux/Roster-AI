from roster.cognitive_planner import CognitivePlanner, CognitivePlanningError


def test_builds_dependency_graph():
    graph = CognitivePlanner().from_specs([
        {"name": "Open notes"},
        {"name": "Read notes", "depends_on": ["1"]},
        {"name": "Summarize", "depends_on": ["2"]},
    ])
    ready = graph.ready()
    assert [step.task.name for step in ready] == ["Open notes"]
    assert graph.ready({graph.plan.steps[0].task.id})[0].task.name == "Read notes"


def test_supports_task_id_dependencies():
    graph = CognitivePlanner().from_specs([
        {"name": "First"},
        {"name": "Second", "depends_on": ["1"]},
    ])
    assert len(graph.plan.steps) == 2


def test_rejects_unknown_dependency():
    try:
        CognitivePlanner().from_specs([
            {"name": "First", "depends_on": ["99"]},
        ])
    except Exception as exc:
        assert isinstance(exc, CognitivePlanningError) or "dependency" in str(exc).lower()
    else:
        raise AssertionError("expected planning error")


def test_metadata_and_priority_survive():
    graph = CognitivePlanner().from_specs([
        {"name": "Research", "priority": 5, "metadata": {"kind": "research"}},
    ])
    task = graph.plan.steps[0].task
    assert task.priority == 5
    assert task.metadata["kind"] == "research"
