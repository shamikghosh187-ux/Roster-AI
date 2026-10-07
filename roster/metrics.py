from dataclasses import dataclass
from threading import Lock
from time import monotonic


@dataclass(frozen=True)
class RuntimeSnapshot:
    submitted: int
    completed: int
    failed: int
    cancelled: int
    active: bool
    last_duration_ms: float | None


class RuntimeMetrics:
    def __init__(self):
        self._lock = Lock()
        self._submitted = 0
        self._completed = 0
        self._failed = 0
        self._cancelled = 0
        self._started_at = None
        self._last_duration_ms = None

    def started(self):
        with self._lock:
            self._submitted += 1
            self._started_at = monotonic()

    def finished(self, status="completed"):
        with self._lock:
            if self._started_at is not None:
                self._last_duration_ms = round((monotonic() - self._started_at) * 1000, 2)
            self._started_at = None
            if status == "failed":
                self._failed += 1
            elif status == "cancelled":
                self._cancelled += 1
            else:
                self._completed += 1

    def snapshot(self):
        with self._lock:
            return RuntimeSnapshot(
                self._submitted,
                self._completed,
                self._failed,
                self._cancelled,
                self._started_at is not None,
                self._last_duration_ms,
            )

    def as_dict(self):
        return self.snapshot().__dict__.copy()
