"""Isolation boundary for memory records by namespace."""
class MemoryNamespace:
    def __init__(self,name):
        clean=name.strip()
        if not clean: raise ValueError("namespace cannot be empty")
        self.name=clean
    def key(self,key):
        clean=key.strip()
        if not clean: raise ValueError("memory key cannot be empty")
        return f"{self.name}:{clean}"
