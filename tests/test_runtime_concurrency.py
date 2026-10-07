from threading import Event, Thread

import pytest

from roster.runtime import AssistantRuntime, RuntimeBusyError


class BlockingAgent:
    def __init__(self):
        self.started = Event()
        self.release = Event()
        self.trace = type("Trace", (), {"as_dicts": lambda self: []})()

    def handle(self, *_args, **_kwargs):
        self.started.set()
        assert self.release.wait(2)
        return True, "ok"


def test_runtime_rejects_concurrent_submission():
    agent = BlockingAgent()
    runtime = AssistantRuntime(agent)
    worker = Thread(target=lambda: runtime.submit("first"))
    worker.start()
    assert agent.started.wait(2)
    try:
        with pytest.raises(RuntimeBusyError):
            runtime.submit("second")
    finally:
        agent.release.set()
        worker.join(2)
    assert not worker.is_alive()
    assert runtime.busy is False
