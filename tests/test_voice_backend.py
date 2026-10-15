import numpy as np
import pytest

from roster.voice_backend import SoundDeviceFrameBackend


class FakeStream:
    def __init__(self, *, callback, **kwargs):
        self.callback = callback
        self.started = False
        self.closed = False

    def start(self):
        self.started = True
        self.callback(np.array([[0.1], [-0.1]], dtype=np.float32), 2, None, None)

    def stop(self):
        pass

    def close(self):
        self.closed = True


class FakeSoundDevice:
    def __init__(self):
        self.stream = None

    def InputStream(self, **kwargs):
        self.stream = FakeStream(**kwargs)
        return self.stream


def test_sounddevice_backend_reads_normalized_frames_and_closes():
    sd = FakeSoundDevice()
    backend = SoundDeviceFrameBackend(backend=sd)
    frame = backend.read(2)
    assert frame.tolist() == pytest.approx([0.1, -0.1])
    backend.close()
    assert sd.stream.closed


def test_closed_backend_cannot_restart():
    backend = SoundDeviceFrameBackend(backend=FakeSoundDevice())
    backend.close()
    with pytest.raises(RuntimeError, match="closed"):
        backend.read(2)
