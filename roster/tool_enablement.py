class ToolEnablement:
    def __init__(self): self._disabled=set()
    def disable(self,name): self._disabled.add(name.strip().lower())
    def enable(self,name): self._disabled.discard(name.strip().lower())
    def is_enabled(self,name): return name.strip().lower() not in self._disabled
    def disabled(self): return tuple(sorted(self._disabled))
