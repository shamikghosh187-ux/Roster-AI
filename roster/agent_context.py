"""Bounded context assembled for an agent decision."""
from dataclasses import dataclass

@dataclass(frozen=True)
class AgentContext:
    messages: tuple[dict,...] = ()
    memories: tuple[object,...] = ()
    sources: tuple[object,...] = ()
    def size_hint(self): return sum(len(str(m.get("content",""))) for m in self.messages)
