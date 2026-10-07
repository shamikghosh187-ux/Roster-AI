from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    chat_model: str = os.getenv("ROSTER_CHAT_MODEL", "openai/gpt-oss-120b")
    vision_model: str = os.getenv("ROSTER_VISION_MODEL", "qwen/qwen3.6-27b")
    whisper_model: str = os.getenv("ROSTER_WHISPER_MODEL", "whisper-large-v3-turbo")
    sample_rate: int = int(os.getenv("ROSTER_SAMPLE_RATE", "16000"))
    record_seconds: int = int(os.getenv("ROSTER_RECORD_SECONDS", "5"))
    noise_gate: float = float(os.getenv("ROSTER_NOISE_GATE", "400"))

    @property
    def groq_api_key(self):
        return os.getenv("GROQ_API_KEY")

settings = Settings()
