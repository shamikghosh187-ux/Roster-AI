"""Session boundary for goal and context state."""
from dataclasses import dataclass, field
from roster.goal import Goal
from roster.agent_context import AgentContext

@dataclass
class AgentSession:
    goal: Goal
    context: AgentContext = field(default_factory=AgentContext)
    step: int = 0
    def advance(self): self.step += 1; return self.step
