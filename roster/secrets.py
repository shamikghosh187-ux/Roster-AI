"""Environment-backed secret access with explicit presence checks."""
import os
class SecretMissingError(RuntimeError): pass
class SecretProvider:
    def __init__(self,environ:dict[str,str]|None=None): self._environ=environ if environ is not None else os.environ
    def require(self,name:str)->str:
        value=self._environ.get(name,"")
        if not value.strip(): raise SecretMissingError(f"required secret is missing: {name}")
        return value
    def optional(self,name:str)->str|None:
        value=self._environ.get(name,""); return value if value.strip() else None
