class ProviderRouter:
    def __init__(self,providers): self.providers=list(providers)
    def call(self,method,*args,**kwargs):
        errors=[]
        for p in self.providers:
            try:return getattr(p,method)(*args,**kwargs)
            except Exception as e: errors.append(f'{type(e).__name__}: {e}')
        raise RuntimeError('all providers failed: '+' | '.join(errors))
    def plan(self,*a,**k): return self.call('plan',*a,**k)
    def chat(self,*a,**k): return self.call('chat',*a,**k)
    def transcribe(self,*a,**k): return self.call('transcribe',*a,**k)
