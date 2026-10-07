import os
import tempfile
import numpy as np
import scipy.io.wavfile as wav
from roster.config import settings

class VoiceIO:
    def __init__(self):
        import pyttsx3
        self.engine = pyttsx3.init()

    def speak(self, text: str):
        text = (text or "").strip()
        if not text: return
        print(f"Roster: {text}")
        self.engine.say(text); self.engine.runAndWait()

    def record(self):
        import sounddevice as sd
        print("\n🎤 Listening...")
        audio = sd.rec(int(settings.record_seconds * settings.sample_rate), samplerate=settings.sample_rate, channels=1, dtype=np.int16)
        sd.wait()
        level=float(np.sqrt(np.mean(audio.astype(np.float32)**2)))
        if level < settings.noise_gate: return None
        fd,path=tempfile.mkstemp(suffix=".wav",prefix="roster-"); os.close(fd)
        wav.write(path,settings.sample_rate,audio)
        return path
