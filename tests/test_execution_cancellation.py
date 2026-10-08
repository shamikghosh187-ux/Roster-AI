import pytest
from roster.cancel import CancellationToken, CancelledError
from roster.execution_cancellation import ensure_not_cancelled

def test_active_token_passes_boundary():
    ensure_not_cancelled(CancellationToken())

def test_cancelled_token_stops_execution():
    token=CancellationToken(); token.cancel()
    with pytest.raises(CancelledError): ensure_not_cancelled(token)
