# Production execution integration

This phase connects Roster's task orchestration primitives to production runtime boundaries.

## Design rules

1. Existing Agent and ToolRegistry APIs remain backward compatible.
2. New orchestration contracts use typed request/result envelopes.
3. Dependency graphs are validated before execution.
4. Runtime settings resolve into explicit execution policy.
5. Sensitive actions pass through a confirmation gate.
6. Execution timing uses an injectable monotonic clock for deterministic tests.

The integration layer is intentionally additive. Later commits will wire these contracts into the existing orchestrator, tool registry, cancellation, retry, tracing, and runtime health systems.
