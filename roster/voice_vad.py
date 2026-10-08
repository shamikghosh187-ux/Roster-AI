"""Small dependency-light voice activity detector."""
from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class VADDecision:
    speech: bool
    started: bool = False
    ended: bool = False
    rms: float = 0.0

class VoiceActivityDetector:
    def __init__(self, *, start_threshold=.025, end_threshold=.015, min_speech_frames=3, end_silence_frames=12):
        if end_threshold > start_threshold:
            raise ValueError("end threshold cannot exceed start threshold")
        if min_speech_frames < 1 or end_silence_frames < 1:
            raise ValueError("frame counts must be positive")
        self.start_threshold = start_threshold
        self.end_threshold = end_threshold
        self.min_speech_frames = min_speech_frames
        self.end_silence_frames = end_silence_frames
        self.reset()

    def reset(self):
        self.active = False
        self._candidate = 0
        self._silence = 0

    @staticmethod
    def rms(samples):
        if samples is None:
            return 0.0

        total = 0.0
        count = 0

        def visit(value):
            nonlocal total, count
            if isinstance(value, (str, bytes)):
                return
            try:
                iterator = iter(value)
            except TypeError:
                number = float(value)
                total += number * number
                count += 1
                return
            for item in iterator:
                visit(item)

        visit(samples)
        return math.sqrt(total / count) if count else 0.0

    def process(self, samples):
        level = self.rms(samples)
        if not self.active:
            if level >= self.start_threshold:
                self._candidate += 1
            else:
                self._candidate = 0
            if self._candidate >= self.min_speech_frames:
                self.active = True
                self._silence = 0
                return VADDecision(True, started=True, rms=level)
            return VADDecision(False, rms=level)

        if level <= self.end_threshold:
            self._silence += 1
            if self._silence >= self.end_silence_frames:
                self.active = False
                self._candidate = 0
                return VADDecision(False, ended=True, rms=level)
        else:
            self._silence = 0
        return VADDecision(True, rms=level)
