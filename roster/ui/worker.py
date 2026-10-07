from PySide6.QtCore import QObject, Signal, Slot

class AgentWorker(QObject):
    started = Signal(str)
    finished = Signal(bool, str)
    failed = Signal(str)
    trace = Signal(str, str)

    def __init__(self, runtime):
        super().__init__()
        self.runtime = runtime
        self.runtime.events.subscribe("trace", self._on_trace)

    @Slot(str)
    def run(self, text: str):
        self.started.emit(text)
        try:
            running, result = self.runtime.submit(text)
            self.finished.emit(running, result)
        except Exception as exc:
            self.failed.emit(str(exc))

    def _on_trace(self, event):
        data = event.payload.get("data", {})
        self.trace.emit(event.payload.get("event", "event"), str(data))
