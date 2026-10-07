from threading import Thread

from roster.cancel import CancellationToken, CancelledError


def test_cancellation_token_is_thread_safe():
    token = CancellationToken()
    worker = Thread(target=token.cancel)
    worker.start()
    worker.join(2)
    assert token.cancelled
    try:
        token.raise_if_cancelled()
        raise AssertionError("expected CancelledError")
    except CancelledError:
        pass
