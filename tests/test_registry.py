from roster.models import Action, Intent
from roster.tools.builtin import ToolExecutor

def test_builtin_registry_contains_all_actions():
    tools = ToolExecutor()
    actions = {spec.action for spec in tools.registry.all()}
    assert actions == set(Action)

def test_registry_marks_side_effects():
    tools = ToolExecutor()
    assert tools.registry.get(Action.OPEN_APP).requires_confirmation is True
    assert tools.registry.get(Action.WHATSAPP).requires_confirmation is True
    assert tools.registry.get(Action.SEARCH).requires_confirmation is False

def test_chat_tool_executes():
    tools = ToolExecutor()
    running, result = tools.execute(Intent(Action.CHAT, "hello"), "hello")
    assert running is True
    assert result == "hello"
