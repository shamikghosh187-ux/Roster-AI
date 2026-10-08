"""Confidence thresholds used to gate automated decisions."""
from dataclasses import dataclass

@dataclass(frozen=True)
class ConfidencePolicy:
    execute_threshold: float = .8
    answer_threshold: float = .5
    def __post_init__(self):
        if not 0 <= self.answer_threshold <= self.execute_threshold <= 1: raise ValueError("invalid confidence thresholds")
    def can_execute(self,confidence): return confidence >= self.execute_threshold
    def can_answer(self,confidence): return confidence >= self.answer_threshold
