"""Production voice configuration and validation."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class VoiceMode(str, Enum):
    PUSH_TO_TALK="push_to_talk"
    WAKE_WORD="wake_word"
    CONTINUOUS="continuous"

class AudioPrivacy(str, Enum):
    SESSION_ONLY="session_only"
    DISABLED="disabled"

@dataclass(frozen=True)
class VoiceSettings:
    enabled: bool=True
    mode: VoiceMode=VoiceMode.PUSH_TO_TALK
    sample_rate: int=16000
    channels: int=1
    frame_ms: int=30
    silence_timeout: float=1.2
    max_listen_seconds: float=20.0
    speech_start_threshold: float=0.025
    speech_end_threshold: float=0.015
    min_speech_frames: int=3
    end_silence_frames: int=12
    input_device: int|None=None
    output_device: int|None=None
    tts_rate: int=185
    tts_volume: float=1.0
    interruptible: bool=True
    privacy: AudioPrivacy=AudioPrivacy.SESSION_ONLY
    wake_phrase: str="roster"
    def __post_init__(self):
        if self.sample_rate < 8000: raise ValueError("sample_rate must be >= 8000")
        if self.channels != 1: raise ValueError("voice capture currently requires mono audio")
        if not 10 <= self.frame_ms <= 100: raise ValueError("frame_ms must be 10..100")
        if self.silence_timeout <= 0 or self.max_listen_seconds <= 0: raise ValueError("timeouts must be positive")
        if self.speech_start_threshold <= 0 or self.speech_end_threshold <= 0: raise ValueError("speech thresholds must be positive")
        if self.speech_end_threshold > self.speech_start_threshold: raise ValueError("end threshold cannot exceed start threshold")
        if self.min_speech_frames < 1 or self.end_silence_frames < 1: raise ValueError("frame counts must be positive")
        if not 80 <= self.tts_rate <= 400: raise ValueError("tts_rate must be 80..400")
        if not 0.0 <= self.tts_volume <= 1.0: raise ValueError("tts_volume must be 0..1")
        if not self.wake_phrase.strip(): raise ValueError("wake_phrase cannot be empty")
