"""Provider-neutral streaming speech interfaces.

Adapters can wrap any STT/TTS provider without putting provider-specific
credentials or network behavior into the voice safety/runtime layer.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Iterable, Callable

@dataclass(frozen=True)
class TranscriptDelta:
    text:str
    final:bool=False
    confidence:float|None=None

class StreamingSTT(Protocol):
    def transcribe_stream(self, frames:Iterable[object], on_delta:Callable[[TranscriptDelta],None]): ...

class StreamingTTS(Protocol):
    def speak_stream(self,text:Iterable[str],on_started=None,on_finished=None): ...

class StreamingSpeechSession:
    def __init__(self,stt=None,tts=None): self.stt=stt; self.tts=tts
    def transcribe(self,frames,on_delta):
        if self.stt is None: raise RuntimeError("streaming STT adapter unavailable")
        return self.stt.transcribe_stream(frames,on_delta)
    def speak(self,chunks,on_started=None,on_finished=None):
        if self.tts is None: raise RuntimeError("streaming TTS adapter unavailable")
        return self.tts.speak_stream(chunks,on_started,on_finished)
