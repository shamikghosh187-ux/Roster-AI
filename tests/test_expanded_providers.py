import json

import pytest

from roster.providers.factory import create_provider, provider_names


EXPECTED_ADDITIONAL = {
    "openrouter", "deepseek", "mistral", "together", "fireworks",
    "cerebras", "sambanova", "perplexity", "nvidia",
}


def test_provider_registry_has_thirteen_real_adapters():
    names = set(provider_names())
    assert EXPECTED_ADDITIONAL <= names
    assert len(names) >= 13


@pytest.mark.parametrize(
    ("name", "env_name"),
    [
        ("openrouter", "OPENROUTER_API_KEY"),
        ("deepseek", "DEEPSEEK_API_KEY"),
        ("mistral", "MISTRAL_API_KEY"),
        ("together", "TOGETHER_API_KEY"),
        ("fireworks", "FIREWORKS_API_KEY"),
        ("cerebras", "CEREBRAS_API_KEY"),
        ("sambanova", "SAMBANOVA_API_KEY"),
        ("perplexity", "PERPLEXITY_API_KEY"),
        ("nvidia", "NVIDIA_API_KEY"),
    ],
)
def test_new_provider_requires_its_own_key(name, env_name, monkeypatch):
    monkeypatch.delenv(env_name, raising=False)
    with pytest.raises(RuntimeError, match="not configured"):
        create_provider(name)


def test_openrouter_adapter_uses_its_key_and_model(monkeypatch):
    from roster.providers import openai_compatible

    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured.update(kwargs)
            class Message:
                content = '{"action":"chat","argument":"hello"}'
            class Choice:
                message = Message()
            class Response:
                choices = [Choice()]
            return Response()

    class FakeClient:
        def __init__(self, api_key, base_url):
            captured["api_key"] = api_key
            captured["base_url"] = base_url
            self.chat = type("Chat", (), {"completions": FakeCompletions()})()

    monkeypatch.setattr(openai_compatible, "OpenAI", FakeClient)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("ROSTER_OPENROUTER_MODEL", "test/model")

    provider = create_provider("openrouter")
    result = provider.plan("say hello")

    assert result.action.value == "chat"
    assert result.argument == "hello"
    assert captured["api_key"] == "test-key"
    assert captured["model"] == "test/model"
    assert captured["base_url"] == "https://openrouter.ai/api/v1"


def test_new_provider_workflow_parser_accepts_json(monkeypatch):
    from roster.providers.openai_compatible import OpenRouterProvider

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    provider = OpenRouterProvider()
    provider._complete = lambda messages: json.dumps({
        "steps": [{
            "name": "respond",
            "action": "chat",
            "argument": "done",
            "depends_on": [],
        }]
    })

    steps = provider.workflow_plan("complete a task")
    assert steps[0]["action"] == "chat"
