import importlib.util
import platform
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class HealthCheck:
    name: str
    ok: bool
    detail: str


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
