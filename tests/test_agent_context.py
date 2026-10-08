from roster.agent_context import AgentContext

def test_context_reports_message_size(): assert AgentContext(messages=({"content":"hello"},)).size_hint()==5
