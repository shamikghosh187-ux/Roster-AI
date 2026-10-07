from threading import Lock

from roster.events import EventBus
from roster.agent import Agent
from roster.cancel import CancellationToken
from roster.metrics import RuntimeMetrics


class RuntimeBusyError(RuntimeError):
    """Raised when a second request is submitted while one is already running."""

class AssistantRuntime:
    """Application-facing runtime that turns Agent internals into observable events."""

    def __init__(self, agent: Agent, events: EventBus | None = None, metrics: RuntimeMetrics | None = None):
        self.agent = agent
        self.events = events or EventBus()
        self.metrics = metrics or RuntimeMetrics()
        self._active_token: CancellationToken | None = None
        self._lock = Lock()

    @property
    def busy(self):
        with self._lock:
            return self._active_token is not None

    def submit(self, text: str):
        text = (text or "").strip()
        if not text:
            return True, ""
        with self._lock:
            if self._active_token is not None:
                raise RuntimeBusyError("A task is already running.")
            self._active_token = CancellationToken()
        self.metrics.started()
        self.events.emit("request_started", text=text)
        try:
            running, result = self.agent.handle(text, cancellation=self._active_token)
            for item in self.agent.trace.as_dicts():
                self.events.emit("trace", **item)
            self.metrics.finished("cancelled" if result == "Task cancelled." else "completed")
            self.events.emit("request_finished", running=running, result=result)
            return running, result
        except Exception as exc:
            self.metrics.finished("failed")
            self.events.emit("request_failed", error=type(exc).__name__, message=str(exc))
            raise
        finally:
            with self._lock:
                self._active_token = None

    def cancel(self):
        with self._lock:
            token = self._active_token
        if token:
            token.cancel()
            self.events.emit("request_cancelled")
