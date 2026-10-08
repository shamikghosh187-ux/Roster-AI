"""Bounded failure analysis and adaptive workflow replanning."""
from __future__ import annotations


class AdaptiveRecovery:
    def __init__(self, provider, planner, max_replans=2):
        if max_replans < 0:
            raise ValueError("max_replans cannot be negative")
        self.provider = provider
        self.planner = planner
        self.max_replans = max_replans

    def replan(self, goal, history, failure, attempt=0):
        if attempt >= self.max_replans:
            raise RuntimeError("adaptive recovery budget exhausted")

        context = {
            "goal": goal,
            "completed": history[-8:],
            "failure": str(failure)[:2000],
            "instruction": (
                "Create a replacement workflow for the remaining goal. "
                "Do not repeat actions already completed unless the failure "
                "evidence proves they must be retried. Keep the workflow minimal "
                "and safe."
            ),
        }
        raw = self.provider.workflow_plan(
            "Recover this task using the supplied execution context:\n"
            + str(context)
        )
        return self.planner.from_specs(raw)
