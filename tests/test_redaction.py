from roster.redaction import redact
def test_redacts_common_secret_shapes():
    safe=redact("api_key=secret123 Bearer abcdefgh")
    assert "secret123" not in safe and "Bearer ***" in safe
