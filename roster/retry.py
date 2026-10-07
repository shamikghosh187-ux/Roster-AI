class TransientToolError(Exception): pass
class PermanentToolError(Exception): pass
class RetryPolicy:
    def __init__(self,attempts=3): self.attempts=max(1,attempts)
    def run(self,fn):
        for i in range(self.attempts):
            try:return fn()
            except TransientToolError:
                if i+1==self.attempts: raise
