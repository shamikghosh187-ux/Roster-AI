import pytest
from roster.agent_plan import AgentPlan
from roster.plan_validator import validate
from roster.subtask import Subtask

def test_validator_accepts_valid_dependencies(): assert validate(AgentPlan("g",(Subtask("a","a"),Subtask("b","b",("a",)))))
def test_validator_rejects_missing_dependency():
    with pytest.raises(ValueError): validate(AgentPlan("g",(Subtask("b","b",("missing",)),)))
