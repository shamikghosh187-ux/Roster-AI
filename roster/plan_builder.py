"""Minimal deterministic plan builder from goal text."""
from roster.agent_plan import AgentPlan
from roster.subtask import Subtask

def build(goal: str):
    clean=goal.strip()
    if not clean: raise ValueError("goal cannot be empty")
    return AgentPlan(clean,(Subtask("goal","Execute the requested goal"),))
