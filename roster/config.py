import os
from dataclasses import dataclass
from pathlib import Path


APP_DIR = Path(os.getenv("ROSTER_DATA_DIR", Path.home() / ".roster"))
APP_DIR.mkdir(parents=True, exist_ok=True)


def _env_float(name, default, minimum=0.0):
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return default
    return value if value >= minimum else default


def _env_int(name, default, minimum=0):
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return value if value >= minimum else default


@dataclass(frozen=True)
class Settings:
    provider: str = os.getenv("ROSTER_PROVIDER", "groq")
    provider_input: str = os.getenv("ROSTER_INPUT_MODE", "auto").strip().lower()
    wake_mode: str = os.getenv("ROSTER_WAKE_MODE", "auto").strip().lower()
    wake_word: str = os.getenv("ROSTER_WAKE_WORD", "hey roster").strip() or "hey roster"
    wake_chunk_seconds: float = _env_float("ROSTER_WAKE_CHUNK_SECONDS", 2.5, 0.1)
    wake_cooldown_seconds: float = _env_float("ROSTER_WAKE_COOLDOWN_SECONDS", 0.5, 0.0)
    chat_model: str = os.getenv("ROSTER_CHAT_MODEL", "openai/gpt-oss-120b")
    vision_model: str = os.getenv("ROSTER_VISION_MODEL", "qwen/qwen3.6-27b")
    whisper_model: str = os.getenv("ROSTER_WHISPER_MODEL", "whisper-large-v3-turbo")
    gemini_model: str = os.getenv("ROSTER_GEMINI_MODEL", "gemini-flash-latest")
    xai_model: str = os.getenv("ROSTER_XAI_MODEL", "grok-4.7")
    claude_model: str = os.getenv("ROSTER_CLAUDE_MODEL", "claude-opus-5-5")
    provider_max_tokens: int = _env_int("ROSTER_PROVIDER_MAX_TOKENS", 4096, 1)
    sample_rate: int = 16000
    record_seconds: int = 5
    noise_gate: int = 400
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    xai_api_key: str = os.getenv("XAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    memory_db_path: str = os.getenv(
        "ROSTER_MEMORY_DB",
        str(APP_DIR / "memory.sqlite3"),
    )


settings = Settings()
