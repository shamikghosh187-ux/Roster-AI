import pytest
from roster.secrets import SecretMissingError,SecretProvider
def test_secret_provider_required_and_optional():
    p=SecretProvider({"TOKEN":"abc","EMPTY":"  "}); assert p.require("TOKEN")=="abc"; assert p.optional("EMPTY") is None
    with pytest.raises(SecretMissingError): p.require("EMPTY")
