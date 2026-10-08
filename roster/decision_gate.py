"""Safety gate combining confidence and confirmation requirements."""
from roster.confidence import ConfidencePolicy
from roster.agent_decision import AgentDecision

def allow(decision: AgentDecision,policy=None):
    policy=policy or ConfidencePolicy()
    if decision.requires_confirmation: return False
    return policy.can_execute(decision.confidence)
