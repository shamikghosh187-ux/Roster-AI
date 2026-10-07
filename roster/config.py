import os
from dataclasses import dataclass
from pathlib import Path


APP_DIR = Path(os.getenv("ROSTER_DATA_DIR", Path.home() / ".roster"))
APP_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class Settings:
    chat_model: str = os.getenv("ROSTER_CHAT_MODEL", "openai/gpt-oss-120b")
    vision_model: str = os.getenv("ROSTER_VISION_MODEL", "qwen/qwen3.6-27b")
    whisper_model: str = os.getenv("ROSTER_WHISPER_MODEL", "whisper-large-v3-turbo")
    sample_rate: int = 16000
    record_seconds: int = 5
    noise_gate: int = 400
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    memory_db_path: str = os.getenv(
        "ROSTER_MEMORY_DB",
        str(APP_DIR / "memory.sqlite3"),
    )


settings = Settings()
