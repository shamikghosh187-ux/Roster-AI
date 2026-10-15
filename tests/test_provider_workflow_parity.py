from types import SimpleNamespace

from roster.providers.claude import ClaudeProvider
from roster.providers.xai import XAIProvider


WORKFLOW_JSON = (
    '{"steps":[{"name":"find files","action":"list_files",'
    '"argument":"C:/\u005ctemp","depends_on":[]}]}'
)


def test_xai_provider_parses_workflow_plan():
    provider = object.__new__(XAIProvider)
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=WORKFLOW_JSON))]
        )

    provider.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )

    steps = provider.workflow_plan("find files", tool_descriptions="list_files")

    assert steps[0]["action"] == "list_files"
    assert captured["messages"][0]["content"].startswith("You are Roster's cognitive workflow planner.")
    assert captured["messages"][-1]["content"] == "find files"


def test_claude_provider_uses_workflow_system_prompt():
    provider = object.__new__(ClaudeProvider)
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=WORKFLOW_JSON)]
        )

    provider.client = SimpleNamespace(messages=SimpleNamespace(create=create))

    steps = provider.workflow_plan("find files", tool_descriptions="list_files")

    assert steps[0]["action"] == "list_files"
    assert captured["system"].startswith("You are Roster's cognitive workflow planner.")
    assert captured["messages"][-1]["content"] == "find files"
