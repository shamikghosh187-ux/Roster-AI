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


def test_workflow_blocks_result_from_reaching_side_effecting_action():
    from roster.workflow_trust import WorkflowTrustBoundaryError

    class Registry:
        def get(self, action):
            return type("Spec", (), {"action": action, "requires_confirmation": True})()

    class Tools:
        def __init__(self):
            self.registry = Registry()
            self.calls = []

        def execute(self, intent, goal, provider, **kwargs):
            self.calls.append((intent.action.value, intent.argument))
            return True, "unexpected"

    class Permissions:
        def requires_confirmation(self, action, registry):
            return False

        def request(self, intent):
            return True

    class Verifier:
        def verify(self, intent, result, **kwargs):
            return type("Verification", (), {"status": "verified", "evidence": "ok"})()

    runner = CognitiveWorkflowExecutor(
        Tools(),
        permissions=Permissions(),
        verifier=Verifier(),
    )

    try:
        runner.execute(
            [
                {"name": "Find", "action": "search", "argument": "report"},
                {
                    "name": "Open",
                    "action": "open_app",
                    "argument": "$RESULT:1",
                    "depends_on": ["1"],
                },
            ],
            "find and open the report",
            provider=object(),
        )
    except WorkflowTrustBoundaryError as exc:
        assert "side-effecting action" in str(exc)
    else:
        raise AssertionError("untrusted result reached a side-effecting action")


def test_unverified_result_is_not_available_to_later_steps():
    class Registry:
        def get(self, action):
            return type("Spec", (), {"action": action, "requires_confirmation": False})()

    class Tools:
        registry = Registry()

        def execute(self, intent, goal, provider, **kwargs):
            return True, "not actually verified"

    class Permissions:
        def requires_confirmation(self, action, registry):
            return False

        def request(self, intent):
            return True

    class Verifier:
        def verify(self, intent, result, **kwargs):
            return type("Verification", (), {"status": "unknown", "evidence": "uncertain"})()

    runner = CognitiveWorkflowExecutor(
        Tools(),
        permissions=Permissions(),
        verifier=Verifier(),
    )

    try:
        runner.execute(
            [
                {"name": "Observe", "action": "search", "argument": "report"},
                {
                    "name": "Read",
                    "action": "read_file",
                    "argument": "$RESULT:1",
                    "depends_on": ["1"],
                },
            ],
            "observe and read",
            provider=object(),
        )
    except RuntimeError as exc:
        assert "verification unknown" in str(exc)
    else:
        raise AssertionError("unknown output was accepted as a workflow result")
