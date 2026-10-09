from roster.voice_devices import AudioDeviceManager
from roster.voice_realtime import RealtimeAudioSession
from roster.voice_barge_in import BargeInController
from roster.voice_streaming import StreamingSpeechSession

class FakeRuntime:
    def __init__(self): self.stops=0
    def stop_speaking(self): self.stops+=1

def test_device_manager_filters_input_output():
    class B:
        def query_devices(self): return [{"name":"mic","max_input_channels":1,"max_output_channels":0,"default_samplerate":16000},{"name":"speaker","max_input_channels":0,"max_output_channels":2,"default_samplerate":48000}]
    m=AudioDeviceManager(B())
    assert len(m.inputs())==1 and len(m.outputs())==1

def test_realtime_frame_size():
    assert RealtimeAudioSession(sample_rate=16000,frame_ms=30).frame_samples==480

def test_barge_in_interrupts_after_consecutive_frames():
    r=FakeRuntime(); b=BargeInController(r,threshold=.1,consecutive_frames=2)
    assert not b.feed_rms(.2)
    assert b.feed_rms(.2)
    assert r.stops==1

def test_streaming_adapter_requires_provider():
    try: StreamingSpeechSession().transcribe([],lambda d:None)
    except RuntimeError: pass
    else: assert False


def test_vad_handles_multichannel_array_like_samples():
    from roster.voice_vad import VoiceActivityDetector
    samples = [[0.1], [-0.1], [0.1], [-0.1]]
    assert VoiceActivityDetector.rms(samples) > 0.09


def test_realtime_session_reports_backend_errors():
    errors = []
    class B:
        def read(self, _):
            raise RuntimeError("device failure")
    session = RealtimeAudioSession(backend=B())
    thread = session.start(lambda _: None, on_error=errors.append)
    thread.join(timeout=1)
    assert errors and isinstance(errors[0], RuntimeError)


def test_realtime_session_rejects_duplicate_start():
    import time
    class B:
        def read(self, _):
            time.sleep(0.05)
            return [0.0]
    session = RealtimeAudioSession(backend=B())
    session.start(lambda _: None)
    try:
        session.start(lambda _: None)
    except RuntimeError:
        pass
    else:
        assert False
    session.stop()
