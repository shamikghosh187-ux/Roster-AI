from roster.adaptive_recovery import AdaptiveRecovery


class Planner:
    def from_specs(self, raw):
        return ("graph", raw)


class Provider:
    def __init__(self):
        self.prompts = []

    def workflow_plan(self, prompt):
        self.prompts.append(prompt)
        return [{"name": "recover", "action": "search", "argument": "retry", "depends_on": []}]


def test_recovery_replans_with_failure_context():
    provider = Provider()
    recovery = AdaptiveRecovery(provider, Planner(), max_replans=2)

    graph = recovery.replan(
        "find the report",
        [{"action": "search", "result": "not found"}],
        "verification failed",
    )

    assert graph[0][0]["name"] == "recover"
    assert "verification failed" in provider.prompts[0]
    assert "find the report" in provider.prompts[0]


def test_recovery_budget_is_bounded():
    recovery = AdaptiveRecovery(Provider(), Planner(), max_replans=1)
    try:
        recovery.replan("goal", [], "failure", attempt=1)
    except RuntimeError as exc:
        assert "budget exhausted" in str(exc)
    else:
        raise AssertionError("unbounded recovery was accepted")
