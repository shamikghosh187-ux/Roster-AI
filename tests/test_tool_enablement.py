from roster.models import Action, Intent
from roster.tool_enablement import ToolEnablement
from roster.tools.builtin import ToolExecutor


def test_tools_can_be_disabled_and_enabled():
    state = ToolEnablement()
    state.disable("Search")
    assert not state.is_enabled("search")
    state.enable("search")
    assert state.is_enabled("search")


def test_builtin_executor_respects_session_tool_disable(monkeypatch):
    executor = ToolExecutor()
    opened = []
    monkeypatch.setattr("roster.tools.builtin.webbrowser.open", lambda url: opened.append(url))

    executor.set_tool_enabled(Action.SEARCH, False)
    should_continue, message = executor.execute(
        Intent(Action.SEARCH, "private query"),
        "search for private query",
    )

    assert should_continue is True
    assert "disabled" in message.lower()
    assert opened == []

    executor.set_tool_enabled(Action.SEARCH, True)
    should_continue, message = executor.execute(
        Intent(Action.SEARCH, "public query"),
        "search for public query",
    )
    assert should_continue is True
    assert "Searching" in message
    assert len(opened) == 1
