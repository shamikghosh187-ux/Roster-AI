from roster.cancel import CancellationToken, CancelledError


def test_cancellation_token_starts_clear():
    token = CancellationToken()
    assert token.cancelled is False


def test_cancellation_token_sets_and_raises():
    token = CancellationToken()
    token.cancel()
    assert token.cancelled is True

    try:
        token.raise_if_cancelled()
    except CancelledError:
        pass
    else:
        raise AssertionError("expected CancelledError")
