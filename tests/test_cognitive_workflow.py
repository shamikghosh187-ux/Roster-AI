from roster.cognitive_workflow import CognitiveWorkflowExecutor


def test_workflow_executes_dependencies_and_resolves_results():
    class Registry:
        def __init__(self):
            self.actions = []

        def get(self, action):
            return type("Spec", (), {"action": action, "requires_confirmation": False})()

    class Tools:
        def __init__(self):
            self.registry = Registry()
            self.calls = []

        def execute(self, intent, goal, provider, **kwargs):
            self.calls.append((intent.action.value, intent.argument))
            if intent.action.value == "search":
                return True, "FOUND: report.txt"
            return False, "READ: important data"

    class Permissions:
        def requires_confirmation(self, action, registry):
            return False

        def request(self, intent):
            raise AssertionError("permission should not be requested")

    class Verifier:
        def verify(self, intent, result, **kwargs):
            return type("Verification", (), {"status": "verified", "failed": False, "evidence": str(result)})()

    tools = Tools()
    runner = CognitiveWorkflowExecutor(tools, permissions=Permissions(), verifier=Verifier())
    running, result, execution = runner.execute(
        [
            {"name": "Find report", "action": "search", "argument": "project report"},
            {
                "name": "Read report",
                "action": "read_file",
                "argument": "$RESULT:1",
                "depends_on": ["1"],
            },
        ],
        "Find and read the report",
        provider=object(),
    )

    assert running is False
    assert tools.calls == [
        ("search", "project report"),
        ("read_file", "FOUND: report.txt"),
    ]
    assert result == "READ: important data"
    assert [item["verification"] for item in execution] == ["verified", "verified"]


def test_workflow_rejects_invalid_action():
    class Tools:
        registry = object()

    runner = CognitiveWorkflowExecutor(Tools())
    try:
        runner.execute(
            [{"name": "Bad", "action": "not_a_real_action"}],
            "test",
            provider=object(),
        )
    except ValueError as exc:
        assert "invalid action" in str(exc)
    else:
        raise AssertionError("invalid workflow action was accepted")
