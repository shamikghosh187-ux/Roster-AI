class Clipboard:
    def __init__(self,backend=None): self.backend=backend or MemoryClipboard()
    def get(self): return self.backend.get()
    def set(self,text): self.backend.set(str(text))
class MemoryClipboard:
    def __init__(self): self.value=''
    def get(self): return self.value
    def set(self,text): self.value=text
