import builtins

import pytest

from roster.audio import VoiceIO
from roster.cancel import CancellationToken, CancelledError
from roster.models import Action, Intent
from roster.providers.router import ProviderRouter
from roster.tools.builtin import ToolExecutor


def test_voice_io_does_not_initialize_tts_at_construction(monkeypatch):
    def fail_import(name, *args, **kwargs):
        if name == "pyttsx3":
            raise AssertionError("TTS must be lazy")
        return original_import(name, *args, **kwargs)

    original_import = builtins.__import__
    monkeypatch.setattr(builtins, "__import__", fail_import)
    voice = VoiceIO()
    assert voice.engine is None


def test_voice_io_speak_degrades_when_tts_backend_is_unavailable(monkeypatch, capsys):
    voice = VoiceIO()

    def fail_import(name, *args, **kwargs):
        if name == "pyttsx3":
            raise RuntimeError("speech backend unavailable")
        return builtins.__import__(name, *args, **kwargs)

    original = builtins.__import__
    monkeypatch.setattr(builtins, "__import__", fail_import)
    voice.speak("hello")
    assert "Roster: hello" in capsys.readouterr().out
    assert voice.engine is None
    monkeypatch.setattr(builtins, "__import__", original)


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

    spec = executor.registry.get(Action.CHAT)
    monkeypatch.setattr(spec, "handler", handler)
    with pytest.raises(CancelledError):
        executor.execute(Intent(action=Action.CHAT, argument="hello"), "hello", cancellation=token)
