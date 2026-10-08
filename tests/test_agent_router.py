from roster.agent_router import route
from roster.intent import Intent

def test_router_maps_intents_to_execution_domains(): assert route(Intent("tool",.9))=="tool"; assert route(Intent("chat",.9))=="conversation"
