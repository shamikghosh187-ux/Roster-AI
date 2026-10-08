"""Bounded recovery strategy selection based on verified historical outcomes.

Memory can influence ranking, but never becomes executable instructions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecoveryStrategy(str, Enum):
    RETRY_ONCE = "retry_once"
    INSPECT_STATE = "inspect_state"
    ALTERNATE_TOOL = "alternate_tool"
    REPLAN = "replan"
    ASK_USER = "ask_user"
    STOP = "stop"


@dataclass(frozen=True)
class StrategyScore:
    strategy: RecoveryStrategy
    score: float
    successes: int
    failures: int
    samples: int


class RecoveryStrategySelector:
    """Select only from a fixed, safety-reviewed strategy vocabulary."""

    def __init__(self, store=None):
        self.store = store

    def score(self, goal, failure, strategy):
        if not isinstance(strategy, RecoveryStrategy):
            strategy = RecoveryStrategy(str(strategy))
        successes = failures = 0
        if self.store is not None:
            row = self.store.recovery_stats(str(goal)[:500], str(failure)[:500], strategy.value)
            if row:
                successes, failures = int(row[0]), int(row[1])
        # Neutral prior. Evidence moves the score by at most 0.4.
        samples = successes + failures
        empirical = ((successes + 1) / (samples + 2)) if samples else 0.5
        score = 0.6 * empirical + 0.4 * 0.5
        return StrategyScore(strategy, round(score, 6), successes, failures, samples)

    def rank(self, goal, failure, allowed=None):
        strategies = list(allowed or RecoveryStrategy)
        ranked = [self.score(goal, failure, strategy) for strategy in strategies]
        return sorted(ranked, key=lambda item: (-item.score, item.strategy.value))

    def choose(self, goal, failure, allowed=None):
        return self.rank(goal, failure, allowed)[0]
