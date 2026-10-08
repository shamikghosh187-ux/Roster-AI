"""Observation-only desktop perception and a typed world model."""
from __future__ import annotations

import base64
import json
import os
import tempfile
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class DesktopElement:
    element_id: str
    role: str
    label: str = ""
    bounds: Optional[tuple[int, int, int, int]] = None
    confidence: float = 0.0


@dataclass(frozen=True)
class DesktopWindow:
    window_id: str
    title: str
    app: str = ""
    bounds: Optional[tuple[int, int, int, int]] = None
    focused: bool = False
    confidence: float = 0.0
    elements: tuple[DesktopElement, ...] = ()


@dataclass(frozen=True)
class DesktopState:
    timestamp: float
    screen_size: tuple[int, int]
    active_window_id: Optional[str] = None
    windows: tuple[DesktopWindow, ...] = ()
    source: str = "local"
    confidence: float = 0.0
    raw_observation: str = field(default="", repr=False)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DesktopPerceptionError(ValueError):
    pass


def _confidence(value: Any) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def _bounds(value: Any) -> Optional[tuple[int, int, int, int]]:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return None
    try:
        result = tuple(int(v) for v in value)
    except (TypeError, ValueError):
        return None
    return result if result[2] >= 0 and result[3] >= 0 else None


def _extract_json(text: str) -> dict[str, Any]:
    value = json.loads(str(text).strip())
    if not isinstance(value, dict):
        raise DesktopPerceptionError("vision provider must return a JSON object")
    return value


def _elements(values: Any) -> tuple[DesktopElement, ...]:
    if not isinstance(values, list):
        return ()
    result = []
    for i, item in enumerate(values[:100]):
        if isinstance(item, dict):
            result.append(
                DesktopElement(
                    element_id=str(item.get("id") or f"element-{i + 1}")[:100],
                    role=str(item.get("role") or "unknown")[:80],
                    label=str(item.get("label") or "")[:300],
                    bounds=_bounds(item.get("bounds")),
                    confidence=_confidence(item.get("confidence")),
                )
            )
    return tuple(result)


def _windows(values: Any) -> tuple[DesktopWindow, ...]:
    if not isinstance(values, list):
        return ()
    result = []
    for i, item in enumerate(values[:30]):
        if isinstance(item, dict):
            result.append(
                DesktopWindow(
                    window_id=str(item.get("id") or f"window-{i + 1}")[:100],
                    title=str(item.get("title") or "")[:300],
                    app=str(item.get("app") or "")[:200],
                    bounds=_bounds(item.get("bounds")),
                    focused=bool(item.get("focused", False)),
                    confidence=_confidence(item.get("confidence")),
                    elements=_elements(item.get("elements")),
                )
            )
    return tuple(result)


class DesktopPerception:
    def __init__(self, provider=None):
        self.provider = provider

    def capture(self, *, reason: str = "observe desktop") -> DesktopState:
        try:
            import pyautogui
        except ImportError as exc:
            raise DesktopPerceptionError("pyautogui is required") from exc

        screen_size = tuple(int(v) for v in pyautogui.size())
        fd, path = tempfile.mkstemp(suffix=".png", prefix="roster-perception-")
        os.close(fd)
        try:
            pyautogui.screenshot(path)
            if self.provider is None:
                return DesktopState(
                    timestamp=time.time(),
                    screen_size=screen_size,
                    source="local",
                    confidence=0.25,
                )

            with open(path, "rb") as handle:
                encoded = base64.b64encode(handle.read()).decode("ascii")

            prompt = (
                "Observe this desktop screenshot only. Never provide commands. "
                "Return ONLY valid JSON: "
                '{"active_window_id": string|null, "windows": [{"id": string, '
                '"title": string, "app": string, "bounds": [x,y,width,height]|null, '
                '"focused": boolean, "confidence": number, "elements": [{"id": string, '
                '"role": string, "label": string, "bounds": [x,y,width,height]|null, '
                '"confidence": number}]}], "confidence": number}. '
                f"Reason: {reason}. Keep labels factual."
            )
            raw = self.provider.vision(prompt, "data:image/png;base64," + encoded)
            parsed = _extract_json(raw)
            return DesktopState(
                timestamp=time.time(),
                screen_size=screen_size,
                active_window_id=(
                    str(parsed["active_window_id"])
                    if parsed.get("active_window_id") is not None
                    else None
                ),
                windows=_windows(parsed.get("windows")),
                source="vision",
                confidence=_confidence(parsed.get("confidence")),
                raw_observation=str(raw)[:4000],
            )
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
