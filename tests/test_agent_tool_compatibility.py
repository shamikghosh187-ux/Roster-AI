from roster.agent import Agent
from roster.models import Action, Intent


class LegacyTools:
    class Registry:
        @staticmethod
        def descriptions():
            return "chat"

        @staticmethod
        def get(action):
            return None

    registry = Registry()

    def __init__(self):
        self.calls = 0

    def execute(self, intent, user_text, provider):
        self.calls += 1
        raise TypeError("handler bug")


class Provider:
    def plan(self, *args, **kwargs):
        return Intent(action=Action.CHAT, argument="hello")


def test_legacy_executor_typeerror_is_not_executed_twice():
    tools = LegacyTools()
    agent = Agent(Provider(), tools)
    try:
        agent.handle("hello")
    except TypeError:
        pass
    assert tools.calls == 1
