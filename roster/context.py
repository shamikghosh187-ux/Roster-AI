class ContextManager:
    def __init__(self,max_messages=24,max_chars=24000): self.max_messages=max_messages; self.max_chars=max_chars
    def trim(self,messages):
        out=[]; total=0
        for m in reversed(list(messages)[-self.max_messages:]):
            n=len(str(m.get('content','')))
            if total+n>self.max_chars: break
            out.append(m); total+=n
        return list(reversed(out))
