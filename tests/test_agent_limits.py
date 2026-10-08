def test_agent_rejects_non_positive_step_limit():
    import pytest
    from roster.agent import Agent
    with pytest.raises(ValueError):
        Agent(object(),object(),max_steps=0)
