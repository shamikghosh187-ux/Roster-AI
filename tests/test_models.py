from roster.models import Action, Intent

def test_action_values():
    assert Action.SEARCH.value == "search"
    assert Intent(Action.CHAT).action is Action.CHAT
