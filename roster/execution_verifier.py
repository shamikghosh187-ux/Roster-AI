"""Post-action verification for the Roster execution loop."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from roster.models import Action, Intent


@dataclass(frozen=True)
class VerificationResult:
    status: str  # verified, failed, unknown
    evidence: str = ""

    @property
    def verified(self) -> bool:
        return self.status == "verified"

    @property
    def failed(self) -> bool:
        return self.status == "failed"

    @property
    def unknown(self) -> bool:
        return self.status == "unknown"


class ExecutionVerifier:
    """Verify completed tool calls without pretending execution implies success."""

    def verify(self, intent: Intent, result: Any, *, goal: str = "", provider=None) -> VerificationResult:
        text = str(result)

        # Tool executors expose failures in a stable human-readable envelope.
        if " tool failed:" in text.lower() or text.lower().startswith("error:"):
            return VerificationResult("failed", text[:500])

        # Read/search operations have observable output: empty/no-match responses
        # are valid results, not execution failures.
        if intent.action in {
            Action.CHAT,
            Action.EXIT,
            Action.SEARCH,
            Action.YOUTUBE,
            Action.LIST_FILES,
            Action.READ_FILE,
            Action.FIND_IN_FILES,
            Action.DESKTOP_STATE,
        }:
            return VerificationResult("verified", text[:500])

        # Desktop actions can optionally be verified from a fresh screen snapshot.
        if intent.action in {Action.OPEN_APP, Action.COMPUTER} and provider is not None:
            try:
                import base64
                import os
                import tempfile
                import pyautogui

                fd, path = tempfile.mkstemp(suffix=".png", prefix="roster-verify-")
                os.close(fd)
                try:
                    pyautogui.screenshot(path)
                    with open(path, "rb") as image_file:
                        encoded = base64.b64encode(image_file.read()).decode("ascii")
                    observation = provider.vision(
                        "Verify whether the requested desktop action succeeded. "
                        f"Goal: {goal}. Requested action: {intent.action.value} "
                        f"{intent.argument}. Return only VERIFIED, FAILED, or UNKNOWN "
                        "followed by brief evidence.",
                        "data:image/png;base64," + encoded,
                    )
                    normalized = str(observation).strip()
                    upper = normalized.upper()
                    if upper.startswith("VERIFIED"):
                        return VerificationResult("verified", normalized[:500])
                    if upper.startswith("FAILED"):
                        return VerificationResult("failed", normalized[:500])
                    return VerificationResult("unknown", normalized[:500])
                finally:
                    try:
                        os.remove(path)
                    except OSError:
                        pass
            except Exception as exc:
                return VerificationResult("unknown", f"screen verification unavailable: {exc}")

        return VerificationResult("unknown", "No deterministic verifier is registered for this action.")
