from roster.redaction import redact
def test_redacts_common_secret_shapes():
    safe=redact("api_key=secret123 Bearer abcdefgh")
    assert "secret123" not in safe and "Bearer ***" in safe


def test_redacts_project_style_keys_and_multiple_secrets():
    safe=redact("key=sk-proj-1234567890123456 api-key=topsecret")
    assert "sk-proj-1234567890123456" not in safe
    assert "topsecret" not in safe
