import pytest

from roster.providers.base import parse_intent
from roster.providers.factory import create_provider, provider_names


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


@pytest.mark.parametrize(
    "name,env_name",
    [
        ("gemini", "GEMINI_API_KEY"),
        ("xai", "XAI_API_KEY"),
        ("claude", "ANTHROPIC_API_KEY"),
        ("groq", "GROQ_API_KEY"),
    ],
)
def test_unconfigured_provider_fails_clearly(name, env_name, monkeypatch):
    monkeypatch.delenv(env_name, raising=False)
    with pytest.raises(RuntimeError, match="not configured"):
        create_provider(name)
