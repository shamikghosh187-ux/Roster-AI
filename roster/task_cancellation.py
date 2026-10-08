from roster.cancel import CancellationToken, CancelledError

def check_cancelled(token: CancellationToken | None):
    if token is not None: token.raise_if_cancelled()
