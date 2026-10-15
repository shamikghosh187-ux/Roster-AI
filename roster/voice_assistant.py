"""Voice-to-cognitive-core bridge with cancellation and interruption semantics."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from roster.cancel import CancellationToken, CancelledError
from roster.voice_runtime import VoiceRuntime

@dataclass(frozen=True)
class VoiceTurn:
    transcript: str
    response: str | None
    status: str

class VoiceAssistantBridge:
    def __init__(self, agent, runtime: VoiceRuntime, *, transcribe: Callable, speak: bool = True):
        self.agent = agent
        self.runtime = runtime
        self.transcribe = transcribe
        self.speak = speak

    def handle_audio(self, *, cancellation=None):
        token = cancellation or CancellationToken()
        transcript = ""
        try:
            frames = self.runtime.capture(cancellation=token)
            token.raise_if_cancelled()
            transcript = str(self.transcribe(frames) or "").strip()
            if not transcript:
                return VoiceTurn("", None, "no_speech")
            token.raise_if_cancelled()
            _, response = self.agent.handle(transcript, cancellation=token)
            token.raise_if_cancelled()
            if self.speak:
                self.runtime.speak(str(response), cancellation=token)
            return VoiceTurn(transcript, str(response), "completed")
        except CancelledError:
            self.runtime.stop_speaking()
            return VoiceTurn(transcript, None, "cancelled")
