from roster.agent_session import AgentSession
from roster.goal import Goal

def test_session_tracks_execution_steps():
    session=AgentSession(Goal("test")); assert session.advance()==1; assert session.step==1
