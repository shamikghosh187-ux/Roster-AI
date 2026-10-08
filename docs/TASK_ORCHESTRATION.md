# Task Orchestration

Roster now has a dedicated orchestration layer for multi-step work.

## Building a plan

Tasks are explicit domain objects. Plans describe dependency edges without executing them. The planner and dependency graph reject missing dependencies and cycles.

## Execution

`TaskOrchestrator` executes dependency-aware plans sequentially and exposes execution tracing. Separate executors support bounded parallel work and timeouts.

## Safety and reliability

Execution policies define confirmation, concurrency, and timeout limits. Tool contracts provide metadata and input validation. Cancellation, retry, recovery, and structured task results are separate boundaries so each can be tested independently.

The existing `ToolRegistry` remains compatible; `registry_adapter.py` provides a bridge into the newer orchestration catalog.
