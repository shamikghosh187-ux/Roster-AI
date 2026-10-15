import threading
import time

from roster.voice_runtime import VoiceRuntime
from roster.voice_settings import VoiceSettings


class FakeTTS:
    def __init__(self):
        self.calls = []
        self.stopped = 0

    def say(self, text):
        self.calls.append(("say", text))

    def runAndWait(self):
        self.calls.append(("wait",))

    def stop(self):
        self.stopped += 1

    def setProperty(self, name, value):
        self.calls.append(("property", name, value))


def test_events_property_returns_immutable_snapshot():
    runtime = VoiceRuntime(VoiceSettings())
    runtime._emit("test_event", value=1)
    snapshot = runtime.events
    runtime._emit("later_event")
    assert len(snapshot) == 1
    assert snapshot[0].kind == "test_event"


def test_wait_for_speech_reports_completion():
    tts = FakeTTS()
    runtime = VoiceRuntime(VoiceSettings(), tts=tts)
    assert runtime.speak("Hey, I'm here.")
    assert runtime.wait_for_speech(timeout=2)
    assert ("say", "Hey, I'm here.") in tts.calls
    assert any(event.kind == "speech_finished" for event in runtime.events)


def test_capture_preserves_frames_used_to_confirm_speech():
    settings = VoiceSettings(
        speech_start_threshold=0.1,
        speech_end_threshold=0.05,
        min_speech_frames=2,
        end_silence_frames=2,
        max_listen_seconds=3,
    )

    class FakeAudio:
        def __init__(self):
            self.frames = iter([
                [0.11, 0.11],
                [0.12, 0.12],
                [0.01, 0.01],
                [0.01, 0.01],
            ])

        def read(self, _):
            return next(self.frames, None)

    runtime = VoiceRuntime(settings, audio=FakeAudio())
    frames = runtime.capture()
    assert frames[:2] == [[0.11, 0.11], [0.12, 0.12]]
    assert len(frames) == 2


def test_stop_closes_audio_backend():
    class FakeAudio:
        closed = False

        def read(self, _):
            return None

        def close(self):
            self.closed = True

    audio = FakeAudio()
    runtime = VoiceRuntime(VoiceSettings(), audio=audio)
    runtime.stop()
    assert audio.closed
