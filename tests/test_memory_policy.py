from roster.memory_policy import MemoryPolicy

def test_policy_filters_disabled_and_sensitive_categories():
    policy=MemoryPolicy(minimum_confidence=.7,allow_profile=False)
    assert not policy.accepts(.6,"fact")
    assert not policy.accepts(.9,"profile")
    assert policy.accepts(.9,"fact")
