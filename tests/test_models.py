from roster.models import Action, ConversationTurn, Intent

def test_action_values_are_stable():
    assert Action.CHAT.value == "chat"
    assert Action.SCREEN_VISION.value == "screen_vision"

def test_intent_defaults():
    intent = Intent(action=Action.CHAT)
    assert intent.argument == ""
    assert intent.metadata == {}

def test_conversation_turn():
    turn = ConversationTurn(role="user", content="hello")
    assert turn.role == "user"
    assert turn.content == "hello"
