import sys
import types

from roster.audio import VoiceIO
from roster.config import settings
from roster.providers.base import SYSTEM_PROMPT, WORKFLOW_PROMPT


def test_roster_chat_prompt_is_friendly_and_voice_natural():
    assert "warm, grounded, friend-like" in SYSTEM_PROMPT
    assert "spoken aloud" in SYSTEM_PROMPT
    assert "never claim human experiences" in SYSTEM_PROMPT
    assert "active conversation" in SYSTEM_PROMPT


def test_workflow_final_reply_is_written_for_speech():
    assert 'argument is the final spoken reply' in WORKFLOW_PROMPT
    assert "conversational" in WORKFLOW_PROMPT


def test_voice_io_applies_configured_tts_settings(monkeypatch):
    calls = []

    class FakeEngine:
        def setProperty(self, name, value):
            calls.append((name, value))

    fake = FakeEngine()
    monkeypatch.setitem(
        sys.modules,
        "pyttsx3",
        types.SimpleNamespace(init=lambda: fake),
    )
    monkeypatch.setattr(
        "roster.audio.settings",
        types.SimpleNamespace(tts_rate=172, tts_volume=0.65),
    )

    voice = VoiceIO()
    assert voice._get_engine() is fake
    assert ("rate", 172) in calls
    assert ("volume", 0.65) in calls


def test_voice_recording_window_defaults_to_conversational_length():
    assert settings.record_seconds >= 15
