"""Health integration for the existing AssistantRuntime boundary."""
from roster.health import HealthCheck, HealthRegistry
from roster.runtime import AssistantRuntime


class RuntimeHealth:
    def __init__(self, runtime: AssistantRuntime) -> None:
        self.runtime = runtime
        self.registry = HealthRegistry()
        self.registry.register("assistant_runtime", self._runtime)
        self.registry.register("agent", self._agent)

    def report(self):
        return self.registry.run()

    def _runtime(self) -> HealthCheck:
        return HealthCheck(
            "assistant_runtime",
            not self.runtime.busy,
            "idle" if not self.runtime.busy else "request active",
        )

    def _agent(self) -> HealthCheck:
        agent = self.runtime.agent
        return HealthCheck(
            "agent",
            agent.provider is not None and agent.tools is not None,
            "provider and tools configured",
        )
