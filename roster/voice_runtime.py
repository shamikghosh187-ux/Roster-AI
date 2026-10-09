"""Interruptible, bounded voice runtime for Roster."""
from __future__ import annotations
import threading
import time
from dataclasses import dataclass
from roster.cancel import CancellationToken, CancelledError
from roster.voice_settings import VoiceSettings
from roster.voice_vad import VoiceActivityDetector

@dataclass(frozen=True)
class VoiceEvent:
    kind: str
    data: dict

class VoiceRuntime:
    def __init__(self, settings=None, *, audio=None, tts=None, clock=time.monotonic, sleep=time.sleep):
        self.settings = settings or VoiceSettings()
        self.audio = audio
        self.tts = tts
        self.clock = clock
        self.sleep = sleep
        self._stop = threading.Event()
        self._speech_lock = threading.Lock()
        self._speech_thread = None
        self.events: list[VoiceEvent] = []

    def _emit(self, kind, **data):
        self.events.append(VoiceEvent(kind, data))

    def stop(self):
        self._stop.set()
        self.stop_speaking()

    def reset(self):
        self._stop.clear()

    def stop_speaking(self):
        with self._speech_lock:
            engine = self.tts
            if engine is not None and hasattr(engine, "stop"):
                try:
                    engine.stop()
                except Exception:
                    pass

    def speak(self, text, *, cancellation=None):
        if not self.settings.enabled or self.tts is None:
            return False
        if not isinstance(text, str) or not text.strip():
            return False
        token = cancellation or CancellationToken()
        self.stop_speaking()

        def run():
            try:
                token.raise_if_cancelled()
                self._emit("speech_started", chars=len(text))
                self.tts.say(text)
                token.raise_if_cancelled()
                self.tts.runAndWait()
                self._emit("speech_finished")
            except CancelledError:
                self.stop_speaking()
                self._emit("speech_cancelled")
            except Exception as exc:
                self._emit("speech_error", error=type(exc).__name__)

        self._speech_thread = threading.Thread(target=run, daemon=True)
        self._speech_thread.start()
        return True

    def apply_tts_settings(self):
        if self.tts is None:
            return
        if hasattr(self.tts, "setProperty"):
            self.tts.setProperty("rate", self.settings.tts_rate)
            self.tts.setProperty("volume", self.settings.tts_volume)

    def capture(self, *, cancellation=None, on_frame=None):
        if not self.settings.enabled or self.audio is None:
            return []
        token = cancellation or CancellationToken()
        vad = VoiceActivityDetector(
            start_threshold=self.settings.speech_start_threshold,
            end_threshold=self.settings.speech_end_threshold,
            min_speech_frames=self.settings.min_speech_frames,
            end_silence_frames=self.settings.end_silence_frames,
        )
        frames = []
        started_at = self.clock()
        self._emit("listening_started", mode=self.settings.mode.value)

        while (
            not self._stop.is_set()
            and self.clock() - started_at < self.settings.max_listen_seconds
        ):
            token.raise_if_cancelled()
            frame = self.audio.read(self.settings.sample_rate * self.settings.frame_ms // 1000)
            if frame is None:
                break
            decision = vad.process(frame)
            if decision.started or decision.speech:
                frames.append(frame)
            if on_frame:
                on_frame(decision)
            if decision.ended and frames:
                break

        self._emit("listening_finished", frames=len(frames))
        return frames
