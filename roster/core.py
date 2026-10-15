import os
import tempfile

import numpy as np
import scipy.io.wavfile as wav

from roster.agent import Agent
from roster.audio import VoiceIO
from roster.config import settings
from roster.memory import ConversationMemory
from roster.intelligent_memory import IntelligentMemory
from roster.providers.factory import create_router
from roster.providers.groq import GroqProvider
from roster.security import PermissionGate
from roster.storage import SQLiteMemoryStore
from roster.tools.builtin import ToolExecutor
from roster.wake import WakeWordListener
from roster.voice_backend import SoundDeviceFrameBackend
from roster.voice_runtime import VoiceRuntime
from roster.voice_settings import VoiceSettings


class Roster:
    def __init__(self):
        # VoiceIO is intentionally lazy: text-only startup must not require a
        # working Windows speech backend.
        self.voice = VoiceIO()
        self.voice_runtime = None
        if settings.voice_runtime_enabled:
            start_threshold = max(0.005, settings.noise_gate / 32768.0)
            runtime_settings = VoiceSettings(
                sample_rate=settings.sample_rate,
                max_listen_seconds=float(settings.record_seconds),
                speech_start_threshold=start_threshold,
                speech_end_threshold=max(0.003, start_threshold * 0.6),
                tts_rate=settings.tts_rate,
                tts_volume=min(1.0, settings.tts_volume),
                wake_phrase=settings.wake_word,
            )
            audio_backend = SoundDeviceFrameBackend(sample_rate=settings.sample_rate)
            tts_engine = self.voice._get_engine()
            self.voice_runtime = VoiceRuntime(runtime_settings, audio=audio_backend, tts=tts_engine)
            self.voice_runtime.apply_tts_settings()
        self.provider = create_router()
        self.memory_store = SQLiteMemoryStore(settings.memory_db_path)
        self.memory = ConversationMemory(store=self.memory_store)
        self.intelligent_memory = IntelligentMemory(self.memory_store)
        self.tools = ToolExecutor()
        self.agent = Agent(
            self.provider,
            self.tools,
            self.memory,
            PermissionGate(),
            intelligent_memory=self.intelligent_memory,
        )

    def _text_input(self):
        try:
            return input("🗣️ You: ").strip()
        except (EOFError, KeyboardInterrupt):
            return ""

    def _run_runtime_voice_once(self):
        """Run one bounded voice turn through the realtime runtime and Groq STT."""
        if not settings.groq_api_key:
            print("Voice runtime requires GROQ_API_KEY for transcription.")
            return True
        audio_path = None
        try:
            frames = self.voice_runtime.capture()
            if not frames:
                return True
            samples = np.concatenate([np.asarray(frame).reshape(-1) for frame in frames])
            pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
            fd, audio_path = tempfile.mkstemp(suffix=".wav", prefix="roster-runtime-")
            os.close(fd)
            wav.write(audio_path, settings.sample_rate, pcm)
            user_text = GroqProvider().transcribe(audio_path).strip()
            if not user_text:
                return True
            print(f"🗣️ You: {user_text}")
            running, result = self.agent.handle(user_text)
            if self.voice_runtime.speak(str(result)):
                # Keep capture and playback serialized until echo-aware
                # full-duplex interruption is available.
                timeout = max(8.0, min(90.0, len(str(result)) / 8.0 + 5.0))
                if not self.voice_runtime.wait_for_speech(timeout):
                    self.voice_runtime.stop_speaking()
            return running
        except KeyboardInterrupt:
            self.voice_runtime.stop()
            return False
        except Exception as exc:
            print(f"❌ Voice runtime error: {exc}")
            self.voice.speak("I had trouble with that. Let's try again.")
            return True
        finally:
            if audio_path:
                try:
                    os.remove(audio_path)
                except OSError:
                    pass

    def run_once(self):
        if self.voice_runtime is not None and settings.provider_input in {"auto", "voice"}:
            return self._run_runtime_voice_once()
        audio_path = None
        try:
            # Explicit voice mode must never silently become text mode. Auto mode
            # is the only mode allowed to fall back when voice is unavailable.
            if settings.provider_input == "voice" and not settings.groq_api_key:
                print("❌ Voice input requires GROQ_API_KEY; staying in voice mode.")
                return True

            transcription_provider = GroqProvider() if settings.groq_api_key else None
            use_voice = settings.provider_input in {"auto", "voice"} and transcription_provider
            if use_voice:
                try:
                    audio_path = self.voice.record()
                except Exception as exc:
                    if settings.provider_input == "voice":
                        raise
                    print(f"⚠️ Voice input unavailable; falling back to text: {exc}")
                    audio_path = None
                    use_voice = False
                if use_voice:
                    if not audio_path:
                        return True
                    try:
                        user_text = transcription_provider.transcribe(audio_path)
                    except Exception as exc:
                        if settings.provider_input == "voice":
                            raise
                        print(
                            f"⚠️ Voice transcription unavailable; falling back to text: {exc}"
                        )
                        user_text = self._text_input()
                else:
                    user_text = self._text_input()
            else:
                user_text = self._text_input()

            if not user_text:
                return True
            print(f"🗣️ You: {user_text}")
            running, result = self.agent.handle(user_text)
            self.voice.speak(result)
            return running
        except Exception as exc:
            print(f"❌ Roster error: {exc}")
            self.voice.speak("I hit an error while handling that request.")
            return True
        finally:
            if audio_path:
                try:
                    os.remove(audio_path)
                except OSError:
                    pass

    def _wake_enabled(self) -> bool:
        if settings.wake_mode in {"off", "disabled", "false", "0"}:
            return False
        if settings.provider_input not in {"auto", "voice"}:
            return False
        return bool(settings.groq_api_key)

    def wait_for_wake_word(self) -> bool:
        if not self._wake_enabled():
            return True
        try:
            return WakeWordListener().wait()
        except Exception as exc:
            if settings.provider_input == "auto":
                print(f"⚠️ Wake word unavailable; continuing without it: {exc}")
                return True
            raise

    def run(self):
        if not self.wait_for_wake_word():
            return
        self.voice.speak("Hey, I'm here. What would you like to talk about?")
        running = True
        try:
            while running:
                running = self.run_once()
        finally:
            if self.voice_runtime is not None:
                self.voice_runtime.stop()
