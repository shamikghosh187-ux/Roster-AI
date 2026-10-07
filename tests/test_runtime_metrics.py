from roster.metrics import RuntimeMetrics
from roster.runtime import AssistantRuntime


class FakeAgent:
    def __init__(self):
        self.trace = type("Trace", (), {"as_dicts": lambda self: []})()

    def handle(self, text, cancellation=None):
        return True, "ok"


def test_runtime_exposes_metrics_after_request():
    runtime = AssistantRuntime(FakeAgent(), metrics=RuntimeMetrics())
    assert runtime.submit("hello") == (True, "ok")
    snapshot = runtime.metrics.snapshot()
    assert snapshot.submitted == 1
    assert snapshot.completed == 1
    assert snapshot.active is False
