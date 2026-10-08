"""Structured goal-state reasoning for bounded agent verification.

Goal state is declarative data, never executable instructions. It lets a
workflow describe what must be true after an action and compare that expected
state with trusted tool results or structured observations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class GoalState:
    conditions: Mapping[str, Any]

    def __post_init__(self):
        if not isinstance(self.conditions, Mapping):
            raise TypeError("goal-state conditions must be a mapping")


@dataclass(frozen=True)
class GoalEvaluation:
    status: str  # satisfied, unsatisfied, unknown
    evidence: str = ""

    @property
    def satisfied(self) -> bool:
        return self.status == "satisfied"


class GoalStateEngine:
    """Compare declarative expected state with observed structured data."""

    def parse(self, raw: Any) -> GoalState | None:
        if raw is None:
            return None
        if not isinstance(raw, Mapping):
            raise ValueError("expected_state must be an object")
        conditions = raw.get("conditions", raw)
        if not isinstance(conditions, Mapping) or not conditions:
            raise ValueError("expected_state must contain non-empty conditions")
        return GoalState(dict(conditions))

    def evaluate(
        self,
        expected: GoalState,
        *,
        result: Any = None,
        observation: Mapping[str, Any] | None = None,
    ) -> GoalEvaluation:
        data = dict(observation or {})
        if result is not None:
            data.setdefault("result", str(result))

        unknown = []
        failures = []
        for path, predicate in expected.conditions.items():
            found, value = self._lookup(data, str(path))
            status = self._check(found, value, predicate)
            if status == "unknown":
                unknown.append(str(path))
            elif status == "unsatisfied":
                failures.append(str(path))

        if failures:
            return GoalEvaluation("unsatisfied", "conditions not met: " + ", ".join(failures[:8]))
        if unknown:
            return GoalEvaluation("unknown", "insufficient evidence for: " + ", ".join(unknown[:8]))
        return GoalEvaluation("satisfied", "all expected-state conditions satisfied")

    @staticmethod
    def _lookup(data: Mapping[str, Any], path: str):
        current: Any = data
        for part in path.split("."):
            if isinstance(current, Mapping) and part in current:
                current = current[part]
            else:
                return False, None
        return True, current

    @staticmethod
    def _check(found: bool, value: Any, predicate: Any) -> str:
        if not isinstance(predicate, Mapping):
            return "satisfied" if found and value == predicate else ("unsatisfied" if found else "unknown")

        if "exists" in predicate:
            expected = bool(predicate["exists"])
            return "satisfied" if found == expected else "unsatisfied"

        if not found:
            return "unknown"

        if "equals" in predicate:
            return "satisfied" if value == predicate["equals"] else "unsatisfied"
        if "not_equals" in predicate:
            return "satisfied" if value != predicate["not_equals"] else "unsatisfied"
        if "contains" in predicate:
            needle = str(predicate["contains"])
            return "satisfied" if needle in str(value) else "unsatisfied"
        if "truthy" in predicate:
            return "satisfied" if bool(value) == bool(predicate["truthy"]) else "unsatisfied"
        return "unknown"
