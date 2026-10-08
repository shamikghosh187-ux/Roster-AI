"""Realtime audio helpers with explicit lifecycle and no persistence."""
from __future__ import annotations
import threading
from dataclasses import dataclass

@dataclass(frozen=True)
class AudioFrame:
    samples: object
    timestamp: float
    sequence: int

class RealtimeAudioSession:
    def __init__(self, *, backend=None, sample_rate=16000, channels=1, frame_ms=30, device=None, clock=None):
        if sample_rate <= 0 or channels <= 0 or frame_ms <= 0:
            raise ValueError("audio configuration must be positive")
        self.backend = backend
        self.sample_rate = sample_rate
        self.channels = channels
        self.frame_ms = frame_ms
        self.device = device
        self.clock = clock or __import__("time").monotonic
        self._stop = threading.Event()
        self._thread = None
        self._sequence = 0

    @property
    def frame_samples(self):
        return self.sample_rate * self.frame_ms // 1000

    def stop(self):
        self._stop.set()

    def start(self, callback, *, on_error=None):
        if self.backend is None:
            raise RuntimeError("audio backend unavailable")
        if not callable(callback):
            raise TypeError("callback must be callable")
        if self._thread is not None and self._thread.is_alive():
            raise RuntimeError("audio session already running")

        self._stop.clear()
        self._sequence = 0

        def run():
            try:
                while not self._stop.is_set():
                    data = self.backend.read(self.frame_samples)
                    if data is None:
                        break
                    frame = AudioFrame(data, self.clock(), self._sequence)
                    self._sequence += 1
                    callback(frame)
            except Exception as exc:
                if on_error is not None:
                    on_error(exc)

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
        return self._thread
