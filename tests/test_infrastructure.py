from datetime import datetime, timedelta, timezone

import pytest

from roster.browser import Browser
from roster.cancel import CancellationToken
from roster.clipboard import Clipboard
from roster.code_search import CodeSearch
from roster.context import ContextManager
from roster.diagnostics import Diagnostics
from roster.editor import FileEditor
from roster.long_memory import LongTermMemory
from roster.plugins import PluginRegistry, PluginTool
from roster.providers.router import ProviderRouter
from roster.scheduler import Scheduler
from roster.state import AgentState, StateMachine
from roster.tasks import TaskEngine
from roster.workspace import Workspace


def test_context_manager_keeps_recent_messages_with_budget():
    manager = ContextManager(max_messages=2, max_chars=20)
    result = manager.trim([
        {"role": "user", "content": "one"},
        {"role": "assistant", "content": "two"},
        {"role": "user", "content": "three"},
    ])
    assert len(result) <= 2
    assert all("content" in item for item in result)


def test_long_term_memory_round_trip(tmp_path):
    memory = LongTermMemory(str(tmp_path / "memory.db"))
    memory.remember("user likes concise answers", "preference")
    rows = memory.search("concise")
    assert rows
    assert rows[0][0] == "user likes concise answers"


def test_workspace_and_code_search(tmp_path):
    (tmp_path / "app.py").write_text("print('roster')\n", encoding="utf-8")
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.js").write_text("roster", encoding="utf-8")
    workspace = Workspace(tmp_path)
    paths = workspace.files()
    assert tmp_path / "app.py" in paths
    assert not any("node_modules" in str(path) for path in paths)
    hits = CodeSearch(workspace).search("roster")
    assert len(hits) == 1
    assert hits[0]["line"] == 1


def test_file_editor_blocks_workspace_escape(tmp_path):
    editor = FileEditor(tmp_path)
    editor.write("nested/test.txt", "hello")
    assert editor.read("nested/test.txt") == "hello"
    assert "hello" in editor.diff("nested/test.txt", "hello world")
    with pytest.raises(PermissionError):
        editor.path("../outside.txt")


def test_browser_rejects_non_http_urls():
    with pytest.raises(ValueError):
        Browser().open("file:///etc/passwd")
    with pytest.raises(ValueError):
        Browser().open("javascript:alert(1)")


def test_clipboard_memory_backend():
    clipboard = Clipboard()
    assert clipboard.get() == ""
    clipboard.set(123)
    assert clipboard.get() == "123"


def test_tasks_and_scheduler():
    engine = TaskEngine()
    task = engine.create("test task")
    engine.set_status(task.id, "running")
    assert engine.list()[0].status == "running"

    scheduler = Scheduler()
    item = scheduler.schedule(task.id, 0)
    assert item.task_id == task.id
    assert scheduler.due(datetime.now(timezone.utc))


def test_plugin_registry():
    registry = PluginRegistry()
    registry.register(PluginTool("echo", "Echo input", lambda args: args["value"], False))
    assert registry.call("echo", {"value": "ok"}) == "ok"
    assert registry.describe()[0]["name"] == "echo"


def test_provider_router_falls_back_and_reports_failure():
    class Broken:
        def chat(self, value):
            raise RuntimeError("broken")

    class Working:
        def chat(self, value):
            return value.upper()

    assert ProviderRouter([Broken(), Working()]).chat("ok") == "OK"
    with pytest.raises(RuntimeError, match="all providers failed"):
        ProviderRouter([Broken()]).chat("ok")


def test_state_and_cancellation_contracts():
    machine = StateMachine()
    assert machine.state == AgentState.IDLE
    machine.move(AgentState.EXECUTING)
    assert machine.state == AgentState.EXECUTING

    token = CancellationToken()
    assert not token.cancelled
    token.cancel()
    assert token.cancelled


def test_diagnostics_report_has_expected_shape():
    report = Diagnostics().report()
    assert report["runtime"] == "python"
    assert isinstance(report["checks"], list)
