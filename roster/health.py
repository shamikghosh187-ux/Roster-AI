"""Runtime health primitives, preserving the legacy health collector."""
import importlib.util
import platform
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable


@dataclass(frozen=True)
class HealthCheck:
    name: str
    ok: bool
    detail: str = ""


def _module(name):
    available = importlib.util.find_spec(name) is not None
    return HealthCheck(name, available, "available" if available else "not installed")


def collect_health():
    checks = [
        _module("numpy"),
        _module("groq"),
        _module("anthropic"),
        _module("google.genai"),
    ]
    return {
        "ok": all(item.ok for item in checks),
        "python": platform.python_version(),
        "platform": sys.platform,
        "checks": [item.__dict__ for item in checks],
    }


@dataclass(frozen=True)
class HealthReport:
    status: str
    checks: tuple[HealthCheck, ...]
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def ready(self) -> bool:
        return self.status == "ready"

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "ready": self.ready,
            "generated_at": self.generated_at,
            "checks": [
                {"name": check.name, "ok": check.ok, "detail": check.detail}
                for check in self.checks
            ],
        }


class HealthRegistry:
    """Register and execute liveness/readiness checks."""

    def __init__(self) -> None:
        self._checks: dict[str, Callable[[], HealthCheck]] = {}

    def register(self, name: str, check: Callable[[], HealthCheck]) -> None:
        normalized = name.strip()
        if not normalized:
            raise ValueError("health check name cannot be empty")
        if normalized in self._checks:
            raise ValueError(f"health check already registered: {normalized}")
        self._checks[normalized] = check

    def run(self) -> HealthReport:
        results: list[HealthCheck] = []
        for name, check in tuple(self._checks.items()):
            try:
                result = check()
                if not isinstance(result, HealthCheck):
                    result = HealthCheck(name, bool(result))
                results.append(result)
            except Exception as exc:
                results.append(HealthCheck(name, False, type(exc).__name__))
        status = "ready" if all(item.ok for item in results) else "degraded"
        return HealthReport(status, tuple(results))

    def names(self) -> tuple[str, ...]:
        return tuple(self._checks)
