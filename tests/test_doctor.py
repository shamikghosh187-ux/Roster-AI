from roster.doctor import diagnose, format_report


def test_doctor_report_never_contains_secret_values():
    report = {
        "ok": True,
        "configuration": {"credentials": {"groq": True}},
        "issues": [],
        "dependencies": {"checks": [{"name": "groq", "ok": True}]},
    }
    output = format_report(report)
    assert "groq: configured" in output
    assert "api_key" not in output.lower()


def test_doctor_flags_missing_key_for_selected_provider(monkeypatch):
    from roster import doctor

    monkeypatch.setattr(
        doctor,
        "public_config",
        lambda: {
            "provider": "groq",
            "credentials": {
                "groq": False, "gemini": False, "xai": False, "anthropic": False,
            },
        },
    )
    monkeypatch.setattr(doctor, "validate_config", lambda: ())
    monkeypatch.setattr(
        doctor.Diagnostics,
        "report",
        lambda self: {"runtime": "python", "checks": [{"name": "groq", "ok": True}]},
    )
    report = diagnose()
    assert not report["ok"]
    assert any("API key is not configured" in item["message"] for item in report["issues"])


def test_doctor_flags_missing_fallback_credentials(monkeypatch):
    from roster import doctor

    monkeypatch.setenv("ROSTER_PROVIDER_FALLBACKS", "gemini,unknown")
    monkeypatch.setattr(
        doctor,
        "public_config",
        lambda: {
            "provider": "groq",
            "credentials": {
                "groq": True, "gemini": False, "xai": False, "anthropic": False,
            },
        },
    )
    monkeypatch.setattr(doctor, "validate_config", lambda: ())
    monkeypatch.setattr(
        doctor.Diagnostics,
        "report",
        lambda self: {"runtime": "python", "checks": [{"name": "groq", "ok": True}]},
    )
    report = diagnose()
    assert not report["ok"]
    assert any(item["field"] == "provider_fallbacks" for item in report["issues"])
