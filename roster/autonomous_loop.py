"""Bounded observe -> decide -> act -> observe controller.

This layer coordinates existing safe tools; it never invents or executes raw
commands. Side-effecting actions still pass through Roster's permission gate.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class LoopObservation:
    phase: str
    data: Any
    verified: bool = False


@dataclass
class AutonomousLoopResult:
    status: str
    cycles: int
    observations: list[LoopObservation] = field(default_factory=list)


class AutonomousObservationLoop:
    """A small deterministic control loop around existing planning/execution."""

    def __init__(self, *, max_cycles: int = 3):
        if max_cycles < 1:
            raise ValueError("max_cycles must be positive")
        self.max_cycles = int(max_cycles)

    def run(
        self,
        *,
        observe: Callable[[], Any],
        decide: Callable[[Any, list[LoopObservation]], Any],
        act: Callable[[Any], Any],
        verify: Callable[[Any, Any], bool],
        cancellation=None,
    ) -> AutonomousLoopResult:
        observations: list[LoopObservation] = []
        for cycle in range(1, self.max_cycles + 1):
            if cancellation:
                cancellation.raise_if_cancelled()

            before = observe()
            observations.append(LoopObservation("before", before, True))

            decision = decide(before, observations[-6:])
            if decision is None:
                return AutonomousLoopResult("complete", cycle, observations)

            if cancellation:
                cancellation.raise_if_cancelled()

            result = act(decision)

            if cancellation:
                cancellation.raise_if_cancelled()

            after = observe()
            verified = bool(verify(decision, after))
            observations.append(LoopObservation("after", after, verified))

            if verified:
                return AutonomousLoopResult("verified", cycle, observations)

        return AutonomousLoopResult("limit_reached", self.max_cycles, observations)
