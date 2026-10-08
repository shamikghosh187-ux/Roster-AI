"""Runtime metrics plus lightweight generic counters/timers.

The original RuntimeMetrics API is kept intact for backwards compatibility.
"""
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


@dataclass(frozen=True)
class MetricSnapshot:
    counters: dict[str, int]
    timings: dict[str, dict[str, float | int]]


class Metrics:
    """Thread-safe generic metrics for infrastructure components."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: dict[str, int] = {}
        self._timings: dict[str, list[float]] = {}

    def increment(self, name: str, amount: int = 1) -> int:
        if amount < 0:
            raise ValueError("metric increment cannot be negative")
        key = self._normalize(name)
        with self._lock:
            self._counters[key] = self._counters.get(key, 0) + amount
            return self._counters[key]

    def observe(self, name: str, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("metric duration cannot be negative")
        key = self._normalize(name)
        with self._lock:
            self._timings.setdefault(key, []).append(float(seconds))

    def snapshot(self) -> MetricSnapshot:
        with self._lock:
            timings = {
                name: {
                    "count": len(values),
                    "total_seconds": sum(values),
                    "max_seconds": max(values),
                }
                for name, values in self._timings.items()
                if values
            }
            return MetricSnapshot(dict(self._counters), timings)

    @staticmethod
    def _normalize(name: str) -> str:
        key = name.strip()
        if not key:
            raise ValueError("metric name cannot be empty")
        return key
