from roster.execution_policy_resolver import ResolvedExecutionPolicy, resolve_execution_policy

class Settings:
    def __init__(self, values): self.values=values
    def get(self, key, default=None): return self.values.get(key, default)

def test_policy_resolver_uses_settings():
    policy = resolve_execution_policy(Settings({
        "assistant.tool_timeout_seconds": 12,
        "performance.max_retries": 3,
        "assistant.confirmation": "never",
        "assistant.max_parallel_tasks": 4,
    }))
    assert policy.timeout_seconds == 12
    assert policy.max_retries == 3
    assert policy.confirmation_required is False
    assert policy.max_parallel_tasks == 4


def test_policy_rejects_invalid_invariants():
    import pytest
    with pytest.raises(ValueError): ResolvedExecutionPolicy(timeout_seconds=0)
    with pytest.raises(ValueError): ResolvedExecutionPolicy(max_retries=-1)
    with pytest.raises(ValueError): ResolvedExecutionPolicy(max_parallel_tasks=0)
