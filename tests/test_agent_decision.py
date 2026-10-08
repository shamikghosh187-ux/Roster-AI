from roster.agent_decision import AgentDecision

def test_agent_decision_preserves_safety_gate():
    decision=AgentDecision("open_app",.9,requires_confirmation=True,rationale="external side effect"); assert decision.requires_confirmation
