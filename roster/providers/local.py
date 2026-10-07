class LocalProvider:
    """Adapter contract for a future local inference runtime."""

    def __init__(self, model="local"):
        self.model=model

    def chat(self, messages):
        raise NotImplementedError("Attach a local chat runtime to LocalProvider.chat().")

    def plan(self, user_text, history=None, tool_descriptions=""):
        raise NotImplementedError("Attach a local planning runtime to LocalProvider.plan().")

    def transcribe(self, audio_path):
        raise NotImplementedError("Attach a local transcription runtime to LocalProvider.transcribe().")
