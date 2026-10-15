"""Audio I/O for Roster with end-of-speech detection.

Voice capture ends after a short silence instead of forcing every utterance
to occupy the entire maximum recording window.
"""
import os
import queue
import tempfile
import time

import numpy as np
import scipy.io.wavfile as wav

from roster.config import settings


class VoiceIO:
    """Audio I/O with lazy TTS initialization and adaptive voice capture."""

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
        """Record one utterance, stopping after speech ends or the time limit.

        A small pre-roll preserves the start of words while VAD waits for
        sustained speech. Temporary audio is returned to the caller, which
        owns deleting it after transcription.
        """
        import sounddevice as sd

        sample_rate = settings.sample_rate
        frame_ms = 30
        frame_samples = max(1, sample_rate * frame_ms // 1000)
        silence_frames_required = max(1, int(1.0 / (frame_ms / 1000)))
        pre_roll_frames = 4
        frames_queue = queue.Queue()
        frames = []
        speech_start = None
        consecutive_speech = 0
        silence_frames = 0
        started_at = time.monotonic()

        def on_audio(indata, frame_count, time_info, status):
            # Copy because PortAudio reuses its callback buffer.
            frames_queue.put(indata.copy())

        print("\n🎤 Listening... (speak naturally; pause when finished)")
        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16,
            blocksize=frame_samples,
            callback=on_audio,
        ):
            while time.monotonic() - started_at < settings.record_seconds:
                try:
                    frame = frames_queue.get(timeout=0.25)
                except queue.Empty:
                    continue
                frames.append(frame)
                level = float(np.sqrt(np.mean(frame.astype(np.float32) ** 2)))
                if level >= settings.noise_gate:
                    consecutive_speech += 1
                    silence_frames = 0
                    if speech_start is None and consecutive_speech >= 2:
                        speech_start = max(0, len(frames) - pre_roll_frames - 1)
                else:
                    consecutive_speech = 0
                    if speech_start is not None:
                        silence_frames += 1
                        if silence_frames >= silence_frames_required:
                            break

        if speech_start is None:
            return None

        audio = np.concatenate(frames[speech_start:], axis=0)
        fd, path = tempfile.mkstemp(suffix=".wav", prefix="roster-")
        os.close(fd)
        try:
            wav.write(path, sample_rate, audio)
        except Exception:
            try:
                os.remove(path)
            except OSError:
                pass
            raise
        return path
