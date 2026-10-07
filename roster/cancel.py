from threading import Event


class CancelledError(Exception):
    pass


class CancellationToken:
    def __init__(self):
        self._event = Event()

    @property
    def cancelled(self):
        return self._event.is_set()

    def cancel(self):
        self._event.set()

    def raise_if_cancelled(self):
        if self._event.is_set():
            raise CancelledError("cancelled")
