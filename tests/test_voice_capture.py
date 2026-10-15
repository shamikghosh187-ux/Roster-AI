import os
import sys
import types

import numpy as np
import scipy.io.wavfile as wav

from roster.audio import VoiceIO


def test_record_stops_after_speech_and_silence(monkeypatch):
    sample_rate = 16000
    frame_samples = sample_rate * 30 // 1000
    silence = np.zeros((frame_samples, 1), dtype=np.int16)
    speech = np.full((frame_samples, 1), 2500, dtype=np.int16)
    pattern = [silence] * 5 + [speech] * 5 + [silence] * 40

    class FakeInputStream:
        def __init__(self, *, callback, **kwargs):
            self.callback = callback

        def __enter__(self):
            for frame in pattern:
                self.callback(frame, len(frame), None, None)
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setitem(
        sys.modules,
        "sounddevice",
        types.SimpleNamespace(InputStream=FakeInputStream),
    )
    path = VoiceIO().record()
    try:
        assert path is not None
        rate, recorded = wav.read(path)
        assert rate == sample_rate
        assert len(recorded) >= frame_samples * 5
        assert len(recorded) < frame_samples * len(pattern)
    finally:
        if path and os.path.exists(path):
            os.remove(path)
