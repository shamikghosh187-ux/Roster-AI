"""Installation diagnostics safe to run before starting the assistant."""
from roster.config_validation import public_config, validate_config
from roster.diagnostics import Diagnostics


def diagnose() -> dict:
    issues = validate_config()
    dependencies = Diagnostics().report()
    return {
        "ok": not issues and all(item["ok"] for item in dependencies["checks"]),
        "configuration": public_config(),
        "issues": [
            {"field": issue.field, "message": issue.message}
            for issue in issues
        ],
        "dependencies": dependencies,
    }


def format_report(report: dict) -> str:
    lines = ["Roster Doctor", "=============", f"Status: {'OK' if report['ok'] else 'ATTENTION REQUIRED'}"]
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
