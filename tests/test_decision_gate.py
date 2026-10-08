from roster.agent_decision import AgentDecision
from roster.decision_gate import allow

def test_gate_blocks_confirmation_required_decisions(): assert not allow(AgentDecision("send",.99,True)); assert allow(AgentDecision("read",.99))
