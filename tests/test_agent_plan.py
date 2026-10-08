from roster.agent_plan import AgentPlan
from roster.subtask import Subtask

def test_plan_exposes_stable_step_ids():
    plan=AgentPlan("goal",(Subtask("a","one"),Subtask("b","two",("a",)))); assert plan.ids()==("a","b")
