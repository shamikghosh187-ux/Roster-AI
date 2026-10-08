import pytest
from roster.cancel import CancellationToken, CancelledError
from roster.task_cancellation import check_cancelled

def test_cancellation_checkpoint_passes_active_token(): check_cancelled(CancellationToken())
def test_cancellation_checkpoint_raises_cancelled_error():
    token=CancellationToken(); token.cancel()
    with pytest.raises(CancelledError): check_cancelled(token)
