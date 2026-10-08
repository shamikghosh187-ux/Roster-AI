from roster.execution_policy_resolver import resolve_execution_policy

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
