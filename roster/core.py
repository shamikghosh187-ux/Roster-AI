import os

from roster.agent import Agent
from roster.audio import VoiceIO
from roster.config import settings
from roster.memory import ConversationMemory
from roster.providers.groq import GroqProvider
from roster.security import PermissionGate
from roster.storage import SQLiteMemoryStore
from roster.tools.builtin import ToolExecutor


class Roster:
    def __init__(self):
        self.voice = VoiceIO()
        self.provider = GroqProvider()
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

    def run_once(self):
        audio_path = self.voice.record()
        if not audio_path:
            return True
        try:
            user_text = self.provider.transcribe(audio_path)
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
            try:
                os.remove(audio_path)
            except OSError:
                pass

    def run(self):
        self.voice.speak("Hello. I am Roster. Your assistant is ready.")
        running = True
        while running:
            running = self.run_once()
