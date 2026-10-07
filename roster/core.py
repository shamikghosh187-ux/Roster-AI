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


class Roster:
    def __init__(self):
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
                audio_path = self.voice.record()
                if not audio_path:
                    return True
                user_text = transcription_provider.transcribe(audio_path)
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

    def run(self):
        self.voice.speak(f"Hello. Roster is ready with {', '.join(self.provider.names)}.")
        running = True
        while running:
            running = self.run_once()
