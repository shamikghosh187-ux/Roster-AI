"""Validated, non-secret configuration reporting."""
from dataclasses import dataclass
from typing import Mapping

from roster.config import settings


SUPPORTED_PROVIDERS = frozenset({"groq", "gemini", "xai", "claude"})
INPUT_MODES = frozenset({"auto", "voice", "text"})
WAKE_MODES = frozenset({"auto", "on", "off", "disabled", "false", "0"})


@dataclass(frozen=True)
class ConfigIssue:
    field: str
    message: str


def validate_config(config=settings) -> tuple[ConfigIssue, ...]:
    issues: list[ConfigIssue] = []

    if config.provider not in SUPPORTED_PROVIDERS:
        issues.append(ConfigIssue("provider", "unsupported provider"))

    if config.provider_input not in INPUT_MODES:
        issues.append(ConfigIssue("provider_input", "unsupported input mode"))

    if config.wake_mode not in WAKE_MODES:
        issues.append(ConfigIssue("wake_mode", "unsupported wake mode"))

    if not config.wake_word.strip():
        issues.append(ConfigIssue("wake_word", "wake word cannot be empty"))

    if config.provider_max_tokens < 1:
        issues.append(ConfigIssue("provider_max_tokens", "must be positive"))

    return tuple(issues)


def public_config(config=settings) -> Mapping[str, object]:
    """Expose operational settings without leaking API credentials."""
    return {
        "provider": config.provider,
        "provider_input": config.provider_input,
        "wake_mode": config.wake_mode,
        "wake_word": config.wake_word,
        "chat_model": config.chat_model,
        "vision_model": config.vision_model,
        "whisper_model": config.whisper_model,
        "provider_max_tokens": config.provider_max_tokens,
        "memory_db_path": config.memory_db_path,
        "credentials": {
            "groq": bool(config.groq_api_key),
            "gemini": bool(config.gemini_api_key),
            "xai": bool(config.xai_api_key),
            "anthropic": bool(config.anthropic_api_key),
        },
    }
