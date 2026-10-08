from roster.confidence import ConfidencePolicy

def test_confidence_policy_distinguishes_execution_and_answering():
    policy=ConfidencePolicy(); assert not policy.can_execute(.7); assert policy.can_answer(.7)
