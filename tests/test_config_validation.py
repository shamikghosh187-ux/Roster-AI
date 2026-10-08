from dataclasses import replace

from roster.config import settings
from roster.config_validation import public_config, validate_config


def test_public_config_does_not_expose_api_keys():
    data = public_config(settings)
    assert "groq_api_key" not in data
    assert data["credentials"]["groq"] in {True, False}


def test_invalid_provider_is_reported():
    invalid = replace(settings, provider="unknown-provider")
    issues = validate_config(invalid)
    assert any(issue.field == "provider" for issue in issues)


def test_default_settings_validate():
    assert validate_config(settings) == ()
