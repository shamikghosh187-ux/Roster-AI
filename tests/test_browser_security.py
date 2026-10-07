from unittest.mock import patch

import pytest

from roster.browser import Browser


def test_browser_rejects_localhost():
    with pytest.raises(ValueError, match="local"):
        Browser().open("http://localhost:8080")


def test_browser_rejects_private_resolved_target():
    with patch("roster.browser.socket.getaddrinfo", return_value=[
        (2, 1, 6, "", ("192.168.1.10", 0))
    ]):
        with pytest.raises(ValueError, match="local or reserved"):
            Browser().open("https://example.com")


def test_browser_rejects_invalid_limit():
    with pytest.raises(ValueError, match="max_bytes"):
        Browser().open("https://example.com", max_bytes=0)
