import os
import tempfile

import numpy as np
import scipy.io.wavfile as wav

from roster.config import settings


class VoiceIO:
    """Audio I/O with lazy TTS initialization so text mode never depends on TTS boot."""

    def __init__(self):
        self.engine = None
        self._tts_error = None

    def _get_engine(self):
        if self.engine is not None:
            return self.engine
        if self._tts_error is not None:
            return None
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
        except Exception as exc:
            self._tts_error = exc
            return None
        return self.engine

    def speak(self, text: str):
        text = (text or "").strip()
        if not text:
            return
        print(f"Roster: {text}")
        engine = self._get_engine()
        if engine is None:
            return
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as exc:
            self._tts_error = exc
            self.engine = None

    def record(self):
        import sounddevice as sd

        print("\n🎤 Listening...")
        audio = sd.rec(
            int(settings.record_seconds * settings.sample_rate),
            samplerate=settings.sample_rate,
            channels=1,
            dtype=np.int16,
        )
        sd.wait()
        level = float(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))
        if level < settings.noise_gate:
            return None
        fd, path = tempfile.mkstemp(suffix=".wav", prefix="roster-")
        os.close(fd)
        wav.write(path, settings.sample_rate, audio)
        return path
