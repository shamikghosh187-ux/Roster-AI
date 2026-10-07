import pytest
from roster.text_utils import normalize_text,truncate
def test_normalize_text_collapses_whitespace(): assert normalize_text("  hello\n   world ")=="hello world"
def test_truncate_respects_limit():
    assert truncate("abcdefgh",5)=="abcd…"
    with pytest.raises(ValueError): truncate("x",0)
