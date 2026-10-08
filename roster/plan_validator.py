"""Validation for dependency-safe agent plans."""
from roster.agent_plan import AgentPlan

def validate(plan: AgentPlan):
    ids=set(plan.ids())
    if len(ids)!=len(plan.steps): raise ValueError("duplicate subtask id")
    for step in plan.steps:
        missing=set(step.depends_on)-ids
        if missing: raise ValueError(f"missing dependencies: {sorted(missing)}")
    return True
