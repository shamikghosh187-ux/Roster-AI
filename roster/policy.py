"""Allow/deny policy primitive for protected actions."""
from dataclasses import dataclass
@dataclass(frozen=True)
class PolicyDecision: allowed:bool; reason:str
class ActionPolicy:
    def __init__(self,denied:set[str]|None=None):
        self._denied={x.strip().upper() for x in (denied or set()) if x.strip()}
    def evaluate(self,action:str)->PolicyDecision:
        normalized=action.strip().upper()
        if not normalized: return PolicyDecision(False,"empty action")
        if normalized in self._denied: return PolicyDecision(False,"action denied by policy")
        return PolicyDecision(True,"action allowed")
