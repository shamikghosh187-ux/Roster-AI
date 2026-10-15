"""Installation diagnostics safe to run before starting the assistant."""
import os

from roster.config_validation import public_config, validate_config
from roster.diagnostics import Diagnostics


_PROVIDER_CREDENTIALS = {
    "groq": "groq",
    "gemini": "gemini",
    "xai": "xai",
    "claude": "anthropic",
    "openrouter": "openrouter",
    "deepseek": "deepseek",
    "mistral": "mistral",
    "together": "together",
    "fireworks": "fireworks",
    "cerebras": "cerebras",
    "sambanova": "sambanova",
    "perplexity": "perplexity",
    "nvidia": "nvidia",
}


def diagnose() -> dict:
    issues = [
        {"field": issue.field, "message": issue.message}
        for issue in validate_config()
    ]
    configuration = public_config()
    credentials = configuration["credentials"]

    provider = configuration["provider"]
    required_credential = _PROVIDER_CREDENTIALS.get(provider)
    if required_credential and not credentials.get(required_credential, False):
        issues.append({
            "field": "credentials",
            "message": f"{provider} is selected but its API key is not configured",
        })

    fallback_names = [
        item.strip().lower()
        for item in os.getenv("ROSTER_PROVIDER_FALLBACKS", "").split(",")
        if item.strip()
    ]
    for fallback in fallback_names:
        credential_name = _PROVIDER_CREDENTIALS.get(fallback)
        if credential_name is None:
            issues.append({
                "field": "provider_fallbacks",
                "message": f"unsupported fallback provider: {fallback}",
            })
        elif not credentials.get(credential_name, False):
            issues.append({
                "field": "provider_fallbacks",
                "message": f"{fallback} is listed as a fallback but its API key is not configured",
            })

    dependencies = Diagnostics().report()
    return {
        "ok": not issues and all(item["ok"] for item in dependencies["checks"]),
        "configuration": configuration,
        "issues": issues,
        "dependencies": dependencies,
    }


def format_report(report: dict) -> str:
    lines = [
        "Roster Doctor",
        "=============",
        f"Status: {'OK' if report['ok'] else 'ATTENTION REQUIRED'}",
    ]
    if report["issues"]:
        lines.append("Configuration issues:")
        lines.extend(f"- {item['field']}: {item['message']}" for item in report["issues"])
    lines.append("Dependencies:")
    lines.extend(
        f"- {item['name']}: {'available' if item['ok'] else 'missing'}"
        for item in report["dependencies"]["checks"]
    )
    credentials = report["configuration"]["credentials"]
    lines.append("Provider credentials:")
    lines.extend(
        f"- {name}: {'configured' if present else 'not configured'}"
        for name, present in credentials.items()
    )
    return "\n".join(lines)
