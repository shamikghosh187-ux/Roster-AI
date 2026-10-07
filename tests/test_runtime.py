from roster.agent import Agent
from roster.runtime import AssistantRuntime, RuntimeBusyError


class FakeProvider:
    def plan(self, *_args, **_kwargs):
        from roster.models import Action, Intent
        return Intent(action=Action.CHAT, argument="hello")


class FakeRegistry:
    def descriptions(self):
        return {}


class FakeTools:
    registry = FakeRegistry()

    def execute(self, *_args):
        return True, "ok"


class FakeMemory:
    def add(self, *_args):
        pass

    def as_messages(self):
        return []


def test_runtime_rejects_concurrent_submission():
    runtime = AssistantRuntime(Agent(FakeProvider(), FakeTools(), memory=FakeMemory()))

    runtime._active_token = object()
    try:
        try:
            runtime.submit("second task")
            raise AssertionError("expected RuntimeBusyError")
        except RuntimeBusyError:
            pass
    finally:
        runtime._active_token = None


def test_runtime_empty_submission_does_not_start_task():
    runtime = AssistantRuntime(Agent(FakeProvider(), FakeTools(), memory=FakeMemory()))

    assert runtime.submit("   ") == (True, "")
    assert runtime.busy is False


def test_runtime_releases_busy_state_after_failure():
    class FailingAgent:
        def handle(self, *_args, **_kwargs):
            raise RuntimeError("boom")

        trace = type("Trace", (), {"as_dicts": lambda self: []})()

    runtime = AssistantRuntime(FailingAgent())

    try:
        runtime.submit("fail")
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected RuntimeError")

    assert runtime.busy is False
