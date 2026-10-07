import os
from roster.audio import VoiceIO
from roster.providers.groq import GroqProvider
from roster.tools.builtin import ToolExecutor

class Roster:
    def __init__(self):
        self.voice = VoiceIO()
        self.provider = GroqProvider()
        self.tools = ToolExecutor()

    def run_once(self):
        audio_path = self.voice.record()
        if not audio_path:
            return True
        try:
            user_text = self.provider.transcribe(audio_path)
            if not user_text:
                return True
            print(f"🗣️ You: {user_text}")
            intent = self.provider.plan(user_text)
            print(f"🧭 Action: {intent.action.value}")
            running, result = self.tools.execute(intent, user_text, self.provider)
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
