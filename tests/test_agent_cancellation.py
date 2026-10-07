from roster.agent import Agent
from roster.cancel import CancellationToken
from roster.models import Action, Intent


class Registry:
    def descriptions(self):
        return {}

    def get(self, _action):
        return None


class Tools:
    registry = Registry()

    def __init__(self):
        self.executed = False

    def execute(self, *_args):
        self.executed = True
        return True, "unexpected"


class Memory:
    def add(self, *_args):
        pass

    def as_messages(self):
        return []


def test_agent_stops_before_execution_when_cancelled():
    token = CancellationToken()
    token.cancel()
    tools = Tools()

    class Provider:
        def plan(self, *_args, **_kwargs):
            return Intent(action=Action.CHAT, argument="hello")

    running, result = Agent(Provider(), tools, memory=Memory()).handle(
        "hello", cancellation=token
    )

    assert running is True
    assert result == "Task cancelled."
    assert tools.executed is False


def test_agent_checks_cancellation_after_planning():
    token = CancellationToken()
    tools = Tools()

    class Provider:
        def plan(self, *_args, **_kwargs):
            token.cancel()
            return Intent(action=Action.SEARCH, argument="hello")

    running, result = Agent(Provider(), tools, memory=Memory()).handle(
        "hello", cancellation=token
    )

    assert running is True
    assert result == "Task cancelled."
    assert tools.executed is False
