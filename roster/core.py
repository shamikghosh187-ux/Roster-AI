import os

from roster.agent import Agent
from roster.audio import VoiceIO
from roster.config import settings
from roster.memory import ConversationMemory
from roster.providers.factory import create_router
from roster.providers.groq import GroqProvider
from roster.security import PermissionGate
from roster.storage import SQLiteMemoryStore
from roster.tools.builtin import ToolExecutor
from roster.wake import WakeWordListener


class Roster:
    def __init__(self):
        # VoiceIO is intentionally lazy: text-only startup must not require a
        # working Windows speech backend.
        self.voice = VoiceIO()
        self.provider = create_router()
        self.memory = ConversationMemory(
            store=SQLiteMemoryStore(settings.memory_db_path)
        )
        self.tools = ToolExecutor()
        self.agent = Agent(
            self.provider,
            self.tools,
            self.memory,
            PermissionGate(),
        )

    def _text_input(self):
        try:
            return input("🗣️ You: ").strip()
        except (EOFError, KeyboardInterrupt):
            return ""

    def run_once(self):
        audio_path = None
        try:
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
                    user_text = transcription_provider.transcribe(audio_path)
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
        self.voice.speak(f"Hello. Roster is ready with {', '.join(self.provider.names)}.")
        running = True
        while running:
            running = self.run_once()
