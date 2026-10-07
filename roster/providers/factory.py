import os

from roster.providers.claude import ClaudeProvider
from roster.providers.gemini import GeminiProvider
from roster.providers.groq import GroqProvider
from roster.providers.xai import XAIProvider


PROVIDERS = {
    "groq": GroqProvider,
    "gemini": GeminiProvider,
    "xai": XAIProvider,
    "claude": ClaudeProvider,
}


def provider_names():
    return tuple(PROVIDERS)


def create_provider(name):
    key = name.strip().lower()
    try:
        provider_type = PROVIDERS[key]
    except KeyError as exc:
        raise ValueError(
            f"Unknown provider '{name}'. Choose one of: {', '.join(PROVIDERS)}"
        ) from exc
    return provider_type()


def create_router():
    from roster.providers.router import ProviderRouter

    primary = os.getenv("ROSTER_PROVIDER", "groq").strip().lower()
    fallback_text = os.getenv("ROSTER_PROVIDER_FALLBACKS", "").strip()
    names = [primary]
    if fallback_text:
        names.extend(item.strip().lower() for item in fallback_text.split(","))
    unique = []
    for name in names:
        if name and name not in unique:
            unique.append(name)

    providers = []
    errors = []
    for name in unique:
        try:
            providers.append(create_provider(name))
        except RuntimeError as exc:
            errors.append(f"{name}: {exc}")

    if not providers:
        detail = "; ".join(errors) or "no providers configured"
        raise RuntimeError(f"No configured AI provider is available: {detail}")
    return ProviderRouter(providers)
