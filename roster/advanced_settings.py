"""Advanced, typed, persistent runtime settings for Roster.

The module is deliberately UI-agnostic so the CLI and future desktop UI can share
one settings contract. Secrets are never persisted by this layer.
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class SettingSpec:
    key: str
    default: Any
    kind: type
    description: str
    restart_required: bool = False
    minimum: float | None = None
    maximum: float | None = None


SPECS: tuple[SettingSpec, ...] = (
    SettingSpec("profile", "default", str, "Active settings profile."),
    SettingSpec("privacy.mode", "standard", str, "Privacy mode: standard, private, or strict."),
    SettingSpec("privacy.telemetry", False, bool, "Allow non-secret local telemetry."),
    SettingSpec("memory.enabled", True, bool, "Enable conversational memory."),
    SettingSpec("memory.retention_days", 90, int, "Maximum retained memory age.", minimum=0, maximum=3650),
    SettingSpec("voice.enabled", True, bool, "Enable voice input/output."),
    SettingSpec("voice.interruptible", True, bool, "Allow speech output to be interrupted."),
    SettingSpec("wake.enabled", True, bool, "Enable wake-word detection."),
    SettingSpec("wake.sensitivity", 0.65, float, "Wake detector sensitivity.", minimum=0.0, maximum=1.0),
    SettingSpec("assistant.autonomy", "balanced", str, "Action autonomy: cautious, balanced, or autonomous."),
    SettingSpec("assistant.confirmation", "smart", str, "Tool confirmation: always, smart, or never."),
    SettingSpec("assistant.max_parallel_tasks", 2, int, "Maximum concurrent background tasks.", minimum=1, maximum=16),
    SettingSpec("assistant.tool_timeout_seconds", 30.0, float, "Default tool execution timeout.", minimum=1.0, maximum=600.0),
    SettingSpec("context.max_messages", 24, int, "Maximum conversational messages in context.", minimum=1, maximum=200),
    SettingSpec("context.max_chars", 24000, int, "Maximum context characters.", minimum=1000, maximum=500000),
    SettingSpec("performance.cache_enabled", True, bool, "Enable safe local caching."),
    SettingSpec("performance.max_retries", 2, int, "Provider retry count.", minimum=0, maximum=8),
    SettingSpec("ui.response_style", "natural", str, "Response style: concise, natural, or detailed."),
)


class SettingsError(ValueError):
    """Raised when a setting key or value is invalid."""


def _spec_map() -> dict[str, SettingSpec]:
    return {spec.key: spec for spec in SPECS}


def _coerce(spec: SettingSpec, value: Any) -> Any:
    if spec.kind is bool:
        if isinstance(value, bool):
            result = value
        elif isinstance(value, str) and value.strip().lower() in {"true", "1", "yes", "on"}:
            result = True
        elif isinstance(value, str) and value.strip().lower() in {"false", "0", "no", "off"}:
            result = False
        else:
            raise SettingsError(f"{spec.key} must be a boolean")
    elif spec.kind is int:
        if isinstance(value, bool):
            raise SettingsError(f"{spec.key} must be an integer")
        try:
            result = int(value)
        except (TypeError, ValueError) as exc:
            raise SettingsError(f"{spec.key} must be an integer") from exc
    elif spec.kind is float:
        try:
            result = float(value)
        except (TypeError, ValueError) as exc:
            raise SettingsError(f"{spec.key} must be a number") from exc
    elif spec.kind is str:
        result = str(value)
    else:
        raise SettingsError(f"unsupported setting type for {spec.key}")

    if spec.minimum is not None and result < spec.minimum:
        raise SettingsError(f"{spec.key} must be >= {spec.minimum}")
    if spec.maximum is not None and result > spec.maximum:
        raise SettingsError(f"{spec.key} must be <= {spec.maximum}")
    return result


class AdvancedSettings:
    """Typed settings with profiles, atomic persistence, and change callbacks."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path or Path.home() / ".roster" / "settings.json").expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._callbacks: list[Callable[[str, Any, Any], None]] = []
        self._data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return raw if isinstance(raw, dict) else {}

    def _save(self) -> None:
        payload = json.dumps(self._data, ensure_ascii=False, indent=2, sort_keys=True)
        fd, temporary = tempfile.mkstemp(prefix=".settings-", suffix=".tmp", dir=self.path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def get(self, key: str, default: Any = None) -> Any:
        spec = _spec_map().get(key)
        if spec is None:
            raise SettingsError(f"unknown setting: {key}")
        return self._data.get(key, spec.default if default is None else default)

    def set(self, key: str, value: Any) -> Any:
        spec = _spec_map().get(key)
        if spec is None:
            raise SettingsError(f"unknown setting: {key}")
        normalized = _coerce(spec, value)
        previous = self.get(key)
        if previous == normalized:
            return normalized
        self._data[key] = normalized
        self._save()
        for callback in tuple(self._callbacks):
            callback(key, previous, normalized)
        return normalized

    def update(self, values: dict[str, Any]) -> dict[str, Any]:
        normalized = {key: _coerce(_spec_map().get(key) or self._unknown(key), value)
                      for key, value in values.items()}
        previous = {key: self.get(key) for key in normalized}
        changed = {key: value for key, value in normalized.items() if previous[key] != value}
        if not changed:
            return normalized
        self._data.update(changed)
        self._save()
        for key, value in changed.items():
            for callback in tuple(self._callbacks):
                callback(key, previous[key], value)
        return normalized

    @staticmethod
    def _unknown(key: str) -> SettingSpec:
        raise SettingsError(f"unknown setting: {key}")

    def reset(self, key: str | None = None) -> None:
        if key is None:
            self._data.clear()
        else:
            if key not in _spec_map():
                raise SettingsError(f"unknown setting: {key}")
            self._data.pop(key, None)
        self._save()

    def snapshot(self, include_defaults: bool = True) -> dict[str, Any]:
        if not include_defaults:
            return dict(self._data)
        return {spec.key: self.get(spec.key) for spec in SPECS}

    def schema(self) -> tuple[SettingSpec, ...]:
        return SPECS

    def on_change(self, callback: Callable[[str, Any, Any], None]) -> None:
        self._callbacks.append(callback)

    def profile(self) -> str:
        return str(self.get("profile"))

    def set_profile(self, name: str) -> None:
        clean = str(name).strip()
        if not clean or any(ch in clean for ch in "/\\"):
            raise SettingsError("profile name must be a non-empty path-safe name")
        self.set("profile", clean)


def public_snapshot(settings: AdvancedSettings | None = None) -> dict[str, Any]:
    """Return settings safe for diagnostics/logging (there are no secret fields)."""
    return (settings or AdvancedSettings()).snapshot()
