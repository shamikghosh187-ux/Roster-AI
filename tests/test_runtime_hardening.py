import builtins

import pytest

from roster.audio import VoiceIO
from roster.cancel import CancellationToken, CancelledError
from roster.models import Action, Intent
from roster.providers.router import ProviderRouter
from roster.tools.builtin import ToolExecutor
from roster.tools.registry import ToolSpec


def test_voice_io_does_not_initialize_tts_at_construction(monkeypatch):
    original = builtins.__import__

    def fail_import(name, *args, **kwargs):
        if name == "pyttsx3":
            raise AssertionError("TTS must be lazy")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_import)
    voice = VoiceIO()
    assert voice.engine is None


def test_voice_io_speak_degrades_when_tts_backend_is_unavailable(monkeypatch, capsys):
    voice = VoiceIO()
    original = builtins.__import__

    def fail_import(name, *args, **kwargs):
        if name == "pyttsx3":
            raise RuntimeError("speech backend unavailable")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_import)
    voice.speak("hello")
    assert "Roster: hello" in capsys.readouterr().out
    assert voice.engine is None


def test_provider_router_does_not_fallback_after_cancellation():
    token = CancellationToken()
    token.cancel()

    class Provider:
        name = "cancelled"

        def plan(self, *args, **kwargs):
            token.raise_if_cancelled()

    router = ProviderRouter([Provider()])
    with pytest.raises(CancelledError):
        router.plan("hello")


def test_builtin_executor_preserves_cancellation():
    token = CancellationToken()
    token.cancel()
    executor = ToolExecutor()
    intent = Intent(action=Action.CHAT, argument="hello")
    with pytest.raises(CancelledError):
        executor.execute(intent, "hello", cancellation=token)


def test_builtin_executor_checks_cancellation_after_handler(monkeypatch):
    token = CancellationToken()
    executor = ToolExecutor()

    def handler(intent, user_text, provider):
        token.cancel()
        return "done"

    monkeypatch.setattr(
        executor.registry,
        "get",
        lambda action: ToolSpec(
            Action.CHAT,
            "chat",
            handler,
        ),
    )
    with pytest.raises(CancelledError):
        executor.execute(
            Intent(action=Action.CHAT, argument="hello"),
            "hello",
            cancellation=token,
        )

def test_open_app_does_not_invoke_cmd_shell(monkeypatch):
    executor = ToolExecutor()
    calls = []

    monkeypatch.setattr("roster.tools.builtin.shutil.which", lambda target: "C:/Windows/notepad.exe")
    monkeypatch.setattr(
        "roster.tools.builtin.subprocess.Popen",
        lambda args, **kwargs: calls.append((args, kwargs)),
    )

    result = executor._open_app(
        Intent(action=Action.OPEN_APP, argument="notepad & whoami"),
        "open it",
        None,
    )

    assert result == "Opening notepad & whoami."
    assert calls == [(["C:/Windows/notepad.exe"], {"shell": False})]
