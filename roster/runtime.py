from roster.events import EventBus
from roster.agent import Agent
from roster.cancel import CancellationToken


class RuntimeBusyError(RuntimeError):
    """Raised when a second request is submitted while one is already running."""


class AssistantRuntime:
    """Application-facing runtime that turns Agent internals into observable events."""

    def __init__(self, agent: Agent, events: EventBus | None = None):
        self.agent = agent
        self.events = events or EventBus()
        self._active_token: CancellationToken | None = None

    @property
    def busy(self):
        return self._active_token is not None

    def submit(self, text: str):
        text = (text or "").strip()
        if not text:
            return True, ""
        if self._active_token is not None:
            raise RuntimeBusyError("A task is already running.")
        self._active_token = CancellationToken()
        self.events.emit("request_started", text=text)
        try:
            running, result = self.agent.handle(text, cancellation=self._active_token)
            for item in self.agent.trace.as_dicts():
                self.events.emit("trace", **item)
            self.events.emit("request_finished", running=running, result=result)
            return running, result
        except Exception as exc:
            self.events.emit("request_failed", error=type(exc).__name__, message=str(exc))
            raise
        finally:
            self._active_token = None

    def cancel(self):
        if self._active_token:
            self._active_token.cancel()
            self.events.emit("request_cancelled")
