from threading import Lock

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
            token = CancellationToken()
            self._active_token = token
        self.events.emit("request_started", text=text)
        try:
            running, result = self.agent.handle(text, cancellation=token)
            for item in self.agent.trace.as_dicts():
                self.events.emit("trace", **item)
            self.events.emit("request_finished", running=running, result=result)
            return running, result
        except Exception as exc:
            self.events.emit("request_failed", error=type(exc).__name__, message=str(exc))
            raise
        finally:
            with self._lock:
                if self._active_token is token:
                    self._active_token = None

    def cancel(self):
        with self._lock:
            token = self._active_token
        if token:
            token.cancel()
            self.events.emit("request_cancelled")
