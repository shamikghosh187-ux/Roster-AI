from roster.models import Action, Intent
from roster.tools.builtin import ToolExecutor

def test_builtin_registry_contains_all_actions():
    tools = ToolExecutor()
    assert {spec.action for spec in tools.registry.all()} == set(Action)

def test_side_effects_are_protected():
    tools = ToolExecutor()
    assert tools.registry.get(Action.OPEN_APP).requires_confirmation
    assert tools.registry.get(Action.WHATSAPP).requires_confirmation
    assert tools.registry.get(Action.COMPUTER).requires_confirmation

def test_chat_tool_executes():
    tools = ToolExecutor()
    running, result = tools.execute(Intent(Action.CHAT, "hello"), "hello")
    assert running is True
    assert result == "hello"
