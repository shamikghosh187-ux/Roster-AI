import pytest

from roster.core import Roster
from roster.providers import factory


class _Voice:
    def record(self):
        return "fake.wav"

    def speak(self, text):
        return None


class _Agent:
    def handle(self, text):
        return True, "ok"


def test_auto_mode_falls_back_to_text_when_transcription_fails(monkeypatch):
    roster = Roster.__new__(Roster)
    roster.voice = _Voice()
    roster.agent = _Agent()

    class BrokenTranscriber:
        def __init__(self):
            pass

        def transcribe(self, path):
            raise RuntimeError("transcription unavailable")

    monkeypatch.setattr("roster.core.GroqProvider", BrokenTranscriber)
    monkeypatch.setattr("roster.core.settings", type(
        "Settings",
        (),
        {"groq_api_key": "configured", "provider_input": "auto"},
    )())
    monkeypatch.setattr(roster, "_text_input", lambda: "hello")

    assert roster.run_once() is True


def test_factory_skips_broken_provider_and_uses_fallback(monkeypatch):
    class BrokenProvider:
        def __init__(self):
            raise ValueError("bad provider configuration")

    class WorkingProvider:
        name = "working"

    monkeypatch.setattr(
        factory,
        "PROVIDERS",
        {"broken": BrokenProvider, "working": WorkingProvider},
    )
    monkeypatch.setenv("ROSTER_PROVIDER", "broken")
    monkeypatch.setenv("ROSTER_PROVIDER_FALLBACKS", "working")

    router = factory.create_router()

    assert router.names == ("working",)
