"""Lightweight microphone wake-word listener for Roster.

The listener uses the existing Groq transcription dependency instead of adding
another always-on speech service. Audio chunks are short and are discarded
after transcription; only the recognized text is used to detect the phrase.
"""

from __future__ import annotations

import os
import re
import tempfile
import time

import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd

from roster.config import settings
from roster.providers.groq import GroqProvider


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _matches_wake_word(text: str, wake_word: str) -> bool:
    heard = _normalize(text)
    target = _normalize(wake_word)
    if not heard or not target:
        return False
    return target in heard


class WakeWordListener:
    """Listen in short chunks until the configured wake phrase is recognized."""

    def __init__(
        self,
        provider: GroqProvider | None = None,
        wake_word: str | None = None,
        chunk_seconds: float | None = None,
        cooldown_seconds: float | None = None,
    ):
        self.provider = provider or GroqProvider()
        self.wake_word = wake_word or settings.wake_word
        self.chunk_seconds = chunk_seconds or settings.wake_chunk_seconds
        self.cooldown_seconds = cooldown_seconds or settings.wake_cooldown_seconds

    def _record_chunk(self) -> str | None:
        samples = int(settings.sample_rate * self.chunk_seconds)
        audio = sd.rec(
            samples,
            samplerate=settings.sample_rate,
            channels=1,
            dtype=np.int16,
        )
        sd.wait()

        level = float(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))
        if level < settings.noise_gate:
            return None

        fd, path = tempfile.mkstemp(suffix=".wav", prefix="roster-wake-")
        os.close(fd)
        wav.write(path, settings.sample_rate, audio)
        return path

    def wait(self) -> bool:
        print(f"🎙️ Waiting for wake word: “{self.wake_word}”")
        while True:
            path = None
            try:
                path = self._record_chunk()
                if not path:
                    continue

                heard = self.provider.transcribe(path)
                print(f"👂 Wake listener heard: {heard}")
                if _matches_wake_word(heard, self.wake_word):
                    print("⚡ Wake word detected.")
                    time.sleep(self.cooldown_seconds)
                    return True
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Wake listener stopped.")
                return False
            except Exception as exc:
                print(f"⚠️ Wake listener: {exc}")
                time.sleep(1)
            finally:
                if path:
                    try:
                        os.remove(path)
                    except OSError:
                        pass
