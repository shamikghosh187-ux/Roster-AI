"""Policy-aware tool execution facade for the production runtime."""
from __future__ import annotations
from roster.execution_clock import ExecutionClock
from roster.execution_gate import ExecutionGate
from roster.execution_result import NormalizedExecutionResult
from roster.task_retry import TaskRetryPolicy, run_with_task_retry
from roster.tool_validation import validate_arguments

class ProductionToolExecutor:
    def __init__(self, catalog, policy, *, clock=None, sleep=None):
        self.catalog=catalog
        self.policy=policy
        self.gate=ExecutionGate(policy)
        self.clock=clock or ExecutionClock()
        self.sleep=sleep

    def execute(self, task_id, tool_name, arguments=None, *, confirmed=False):
        started=self.clock.now()
        tool=self.catalog.get(tool_name)
        if tool is None:
            return NormalizedExecutionResult.failed(task_id, f"unknown tool: {tool_name}", self.clock.elapsed_ms(started))
        decision=self.gate.check(sensitive=tool.sensitive, confirmed=confirmed)
        if not decision.allowed:
            return NormalizedExecutionResult.failed(task_id, decision.reason, self.clock.elapsed_ms(started))
        try:
            values=validate_arguments(tool.input_schema, arguments or {})
            if tool.handler is None:
                raise RuntimeError(f"tool has no handler: {tool.name}")
            retry=TaskRetryPolicy(self.policy.max_retries + 1, 0.0)
            kwargs={} if self.sleep is None else {"sleep": self.sleep}
            value=run_with_task_retry(lambda: tool.handler(values, None), retry, **kwargs)
            return NormalizedExecutionResult.completed(task_id, value, self.clock.elapsed_ms(started))
        except Exception as exc:
            return NormalizedExecutionResult.failed(task_id, str(exc), self.clock.elapsed_ms(started))
