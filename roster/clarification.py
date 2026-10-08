"""Ambiguity detection boundary for underspecified requests."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Clarification:
    needed: bool
    reason: str = ""

def assess(text: str) -> Clarification:
    clean=(text or "").strip()
    if not clean: return Clarification(True,"empty request")
    if len(clean.split()) <= 1 and clean.lower() not in {"hi","hello","thanks"}: return Clarification(True,"request is underspecified")
    return Clarification(False)
