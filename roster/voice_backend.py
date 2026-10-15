"""Concrete sounddevice input adapter for the provider-neutral voice runtime."""
from __future__ import annotations

import queue
import threading


class SoundDeviceFrameBackend:
    """Read normalized mono float frames with bounded buffering.

    Audio is held only in a small in-memory queue and is discarded as soon as
    the consumer reads it or the session closes.
    """

    def __init__(self, *, sample_rate=16000, channels=1, device=None, queue_frames=8, backend=None):
        if sample_rate < 8000 or channels != 1 or queue_frames < 1:
            raise ValueError("invalid audio backend configuration")
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device
        self._sd = backend
        self._queue = queue.Queue(maxsize=queue_frames)
        self._lock = threading.RLock()
        self._stream = None
        self._error = None
        self._closed = False

    def _ensure_started(self, frame_samples):
        with self._lock:
            if self._closed:
                raise RuntimeError("audio backend is closed")
            if self._stream is not None:
                return
            if self._sd is None:
                import sounddevice as sd
                self._sd = sd

            def on_audio(indata, frame_count, time_info, status):
                if status:
                    self._error = RuntimeError("microphone stream reported an audio status")
                frame = indata.copy().reshape(-1)
                try:
                    self._queue.put_nowait(frame)
                except queue.Full:
                    # Keep recent audio rather than allowing latency to grow.
                    try:
                        self._queue.get_nowait()
                    except queue.Empty:
                        pass
                    try:
                        self._queue.put_nowait(frame)
                    except queue.Full:
                        pass

            self._stream = self._sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                blocksize=frame_samples,
                device=self.device,
                callback=on_audio,
            )
            self._stream.start()

    def read(self, frame_samples):
        if frame_samples < 1:
            raise ValueError("frame_samples must be positive")
        self._ensure_started(frame_samples)
        if self._error is not None:
            error, self._error = self._error, None
            raise error
        try:
            return self._queue.get(timeout=0.25)
        except queue.Empty:
            # Brief callback gaps count as silence, not end-of-stream.
            return [0.0] * frame_samples

    def close(self):
        with self._lock:
            self._closed = True
            stream, self._stream = self._stream, None
            if stream is not None:
                try:
                    stream.stop()
                finally:
                    stream.close()
            while True:
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    break
