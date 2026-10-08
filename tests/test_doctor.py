from roster.doctor import format_report


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
