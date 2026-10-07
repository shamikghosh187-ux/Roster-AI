from roster.policy import ActionPolicy
def test_policy_denies_configured_action():
    p=ActionPolicy({"computer"}); assert not p.evaluate(" COMPUTER ").allowed; assert p.evaluate("chat").allowed
