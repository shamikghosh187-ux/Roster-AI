import os

import pytest

from roster.providers.factory import create_provider, create_router, provider_names
from roster.providers.base import parse_intent


def test_provider_catalog():
    assert {"groq", "gemini", "xai", "claude"} <= set(provider_names())


@pytest.mark.parametrize(
    "raw,expected",
    [
        ('{"action":"chat","argument":"hello"}', "chat"),
        ('{"action":"search","argument":"Python"}', "search"),
        ("not json", "chat"),
    ],
)
def test_provider_intent_parser(raw, expected):
    assert parse_intent(raw).action.value == expected


def test_unknown_provider_has_clear_error():
    with pytest.raises(ValueError, match="Unknown provider"):
        create_provider("not-a-provider")


def test_factory_requires_a_configured_provider(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("ROSTER_PROVIDER", "gemini")
    import roster.config
    monkeypatch.setattr(roster.config.settings, "gemini_api_key", "", raising=False)
    with pytest.raises(RuntimeError, match="No configured AI provider"):
        create_router()


def test_provider_input_mode_is_safe():
    assert os.getenv("ROSTER_INPUT_MODE", "auto") in {"auto", "voice", "text"}
