from roster.runtime import AssistantRuntime
from roster.runtime_health import RuntimeHealth


class DummyAgent:
    provider = object()
    tools = object()
    trace = type("Trace", (), {"as_dicts": lambda self: []})()


def test_runtime_health_is_ready_when_runtime_is_idle():
    report = RuntimeHealth(AssistantRuntime(DummyAgent())).report()
    assert report.ready
    assert {check.name for check in report.checks} == {"assistant_runtime", "agent"}
