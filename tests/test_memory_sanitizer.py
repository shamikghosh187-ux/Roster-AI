import pytest
from roster.memory_sanitizer import sanitize

def test_sanitizer_rejects_secret_like_values():
    with pytest.raises(ValueError): sanitize("token sk-abcdefghijklmnopqrstuvwxyz")

def test_sanitizer_preserves_normal_text(): assert sanitize("  hello  ")=="hello"
