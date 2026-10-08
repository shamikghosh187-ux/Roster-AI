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
    with patch("roster.browser.build_opener",return_value=opener):
        with patch.object(Browser,"_validate_target",wraps=Browser()._validate_target) as validate:
            with pytest.raises(ValueError,match="local"):
                Browser().open("https://public.example")
            assert validate.call_count==2
            assert validate.call_args_list[-1].args[0]=="http://127.0.0.1:8080/private"

def test_browser_rejects_negative_redirect_limit():
    with pytest.raises(ValueError,match="redirects"):
        Browser().open("https://example.com",max_redirects=-1)
