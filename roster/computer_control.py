"""Safe, structured desktop-control primitives for Roster.

The controller deliberately exposes a small allow-listed action vocabulary instead of
accepting arbitrary Python/shell commands. Higher-level planning can compose these
operations, while the permission gate remains responsible for sensitive actions.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


_ALLOWED_OPERATIONS = {
    "move",
    "click",
    "double_click",
    "right_click",
    "drag",
    "type",
    "press",
    "hotkey",
    "scroll",
}


@dataclass(frozen=True)
class ComputerCommand:
    operation: str
    value: str


class ComputerCommandError(ValueError):
    pass


def parse_computer_command(argument: str) -> ComputerCommand:
    raw = str(argument or "").strip()
    if not raw:
        raise ComputerCommandError(
            "computer action required; use move x,y | click x,y | double_click x,y | "
            "right_click x,y | drag x1,y1 to x2,y2 | type text | press key | hotkey key1+key2 | scroll amount"
        )
    parts = raw.split(maxsplit=1)
    operation = parts[0].lower()
    value = parts[1].strip() if len(parts) == 2 else ""
    if operation not in _ALLOWED_OPERATIONS:
        raise ComputerCommandError(f"unsupported computer operation: {operation}")
    if not value:
        raise ComputerCommandError(f"{operation} requires an argument")
    return ComputerCommand(operation, value)


def _point(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(-?\d+)\s*,\s*(-?\d+)\s*", value)
    if not match:
        raise ComputerCommandError("coordinates must use x,y")
    return int(match.group(1)), int(match.group(2))


def _drag_points(value: str) -> tuple[tuple[int, int], tuple[int, int]]:
    match = re.fullmatch(
        r"\s*(-?\d+)\s*,\s*(-?\d+)\s+to\s+(-?\d+)\s*,\s*(-?\d+)\s*",
        value,
        flags=re.IGNORECASE,
    )
    if not match:
        raise ComputerCommandError("drag coordinates must use x1,y1 to x2,y2")
    return (int(match.group(1)), int(match.group(2))), (int(match.group(3)), int(match.group(4)))


def execute_computer_command(command: ComputerCommand, *, pyautogui_module: Any = None) -> str:
    if pyautogui_module is None:
        import pyautogui as pyautogui_module

    operation = command.operation
    value = command.value

    if operation == "move":
        x, y = _point(value)
        pyautogui_module.moveTo(x, y, duration=0.15)
        return f"Moved pointer to ({x}, {y})."

    if operation == "click":
        x, y = _point(value)
        pyautogui_module.click(x, y)
        return f"Clicked at ({x}, {y})."

    if operation == "double_click":
        x, y = _point(value)
        pyautogui_module.doubleClick(x, y, interval=0.08)
        return f"Double-clicked at ({x}, {y})."

    if operation == "right_click":
        x, y = _point(value)
        pyautogui_module.rightClick(x, y)
        return f"Right-clicked at ({x}, {y})."

    if operation == "drag":
        (x1, y1), (x2, y2) = _drag_points(value)
        pyautogui_module.moveTo(x1, y1, duration=0.1)
        pyautogui_module.dragTo(x2, y2, duration=0.25, button="left")
        return f"Dragged from ({x1}, {y1}) to ({x2}, {y2})."

    if operation == "type":
        pyautogui_module.write(value, interval=0.01)
        return "Typed the requested text."

    if operation == "press":
        keys = [item.strip().lower() for item in value.split(",") if item.strip()]
        if len(keys) != 1:
            raise ComputerCommandError("press accepts one key; use hotkey for combinations")
        pyautogui_module.press(keys[0])
        return f"Pressed {keys[0]}."

    if operation == "hotkey":
        keys = [item.strip().lower() for item in value.split("+") if item.strip()]
        if not keys:
            raise ComputerCommandError("hotkey requires at least one key")
        if len(keys) > 5:
            raise ComputerCommandError("hotkey supports at most five keys")
        pyautogui_module.hotkey(*keys)
        return f"Pressed {'+'.join(keys)}."

    if operation == "scroll":
        try:
            amount = int(value)
        except ValueError as exc:
            raise ComputerCommandError("scroll amount must be an integer") from exc
        if abs(amount) > 20:
            raise ComputerCommandError("scroll amount must be between -20 and 20")
        pyautogui_module.scroll(amount)
        return f"Scrolled {amount}."

    raise ComputerCommandError(f"unsupported computer operation: {operation}")
