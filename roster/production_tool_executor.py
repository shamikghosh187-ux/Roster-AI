"""Policy-aware tool execution facade for the production runtime."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

from roster.cancel import CancelledError
from roster.execution_cancellation import ensure_not_cancelled
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

    def execute_request(self, invocation, *, confirmed=False, cancellation=None, context=None):
        return self.execute(
            invocation.task_id or "",
            invocation.tool_name,
            invocation.arguments,
            confirmed=confirmed,
            cancellation=cancellation,
            context=context,
        )

    def execute(self, task_id, tool_name, arguments=None, *, confirmed=False, cancellation=None, context=None):
        started=self.clock.now()
        ensure_not_cancelled(cancellation)
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
            def operation():
                ensure_not_cancelled(cancellation)
                return tool.handler(values, context)
            if self.policy.timeout_seconds > 0:
                pool=ThreadPoolExecutor(max_workers=1)
                future=pool.submit(lambda: run_with_task_retry(operation, retry, **kwargs))
                try:
                    value=future.result(timeout=self.policy.timeout_seconds)
                except FutureTimeout as exc:
                    future.cancel()
                    raise TimeoutError(f"tool execution exceeded {self.policy.timeout_seconds}s") from exc
                finally:
                    pool.shutdown(wait=False, cancel_futures=True)
            else:
                value=run_with_task_retry(operation, retry, **kwargs)
            ensure_not_cancelled(cancellation)
            return NormalizedExecutionResult.completed(task_id, value, self.clock.elapsed_ms(started))
        except CancelledError:
            raise
        except Exception as exc:
            return NormalizedExecutionResult.failed(task_id, str(exc), self.clock.elapsed_ms(started))
