from unittest.mock import Mock,patch
from urllib.error import HTTPError

import pytest

from roster.browser import Browser

def test_browser_validates_redirect_target_before_following():
    response=HTTPError(
        "https://public.example",
        302,
        "redirect",
        {"Location":"http://127.0.0.1:8080/private"},
        None,
    )
    opener=Mock()
    opener.open.side_effect=response

    def resolve(host,*args,**kwargs):
        address="127.0.0.1" if host == "127.0.0.1" else "93.184.216.34"
        return [(2,1,6,"",(address,0))]

    with patch("roster.browser.build_opener",return_value=opener):
        with patch("roster.browser.socket.getaddrinfo",side_effect=resolve):
            with pytest.raises(ValueError,match="local"):
                Browser().open("https://public.example")
    assert opener.open.call_count==1

def test_browser_rejects_negative_redirect_limit():
    with pytest.raises(ValueError,match="redirects"):
        Browser().open("https://example.com",max_redirects=-1)
