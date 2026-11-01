import pytest

from roster.models import Action
from roster.providers.base import parse_intent, parse_workflow


@pytest.mark.parametrize(
    "raw",
    [
        "not json",
        '["chat", "hello"]',
        '"hello"',
        "42",
        "null",
    ],
)
def test_parse_intent_falls_back_to_chat_for_non_object_responses(raw):
    intent = parse_intent(raw)

    assert intent.action is Action.CHAT
    assert intent.argument == raw
    assert intent.metadata == {}


def test_parse_intent_parses_valid_intent_and_metadata():
    intent = parse_intent(
        '{"action":"search","argument":"  astronomy  ","metadata":{"source":"test"}}'
    )

    assert intent.action is Action.SEARCH
    assert intent.argument == "astronomy"
    assert intent.metadata == {"source": "test"}


def test_parse_intent_uses_chat_for_unknown_action():
    intent = parse_intent('{"action":"not_a_real_action","argument":"hello"}')

    assert intent.action is Action.CHAT
    assert intent.argument == "hello"


def test_parse_intent_handles_none_without_crashing():
    intent = parse_intent(None)

    assert intent.action is Action.CHAT
    assert intent.argument == ""


def test_parse_workflow_accepts_top_level_step_list():
    steps = [{"name": "say hello", "action": "chat", "argument": "hello", "depends_on": []}]

    assert parse_workflow(
        '[{"name":"say hello","action":"chat","argument":"hello","depends_on":[]}]'
    ) == steps


def test_parse_workflow_accepts_steps_object():
    steps = [{"name": "say hello", "action": "chat", "argument": "hello", "depends_on": []}]

    assert parse_workflow(
        '{"steps":[{"name":"say hello","action":"chat","argument":"hello","depends_on":[]}]}'
    ) == steps


@pytest.mark.parametrize("raw", ["not json", "{}", "null", "42", '"steps"'])
def test_parse_workflow_rejects_invalid_workflow_shapes(raw):
    with pytest.raises(ValueError):
        parse_workflow(raw)


def test_parse_workflow_rejects_non_string_input_as_invalid_json_shape():
    with pytest.raises(ValueError):
        parse_workflow(42)
