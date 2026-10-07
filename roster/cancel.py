class CancelledError(Exception): pass
class CancellationToken:
    def __init__(self): self.cancelled=False
    def cancel(self): self.cancelled=True
    def raise_if_cancelled(self):
        if self.cancelled: raise CancelledError('cancelled')
