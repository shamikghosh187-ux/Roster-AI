"""Environment-independent feature flag registry."""
class FeatureFlags:
    def __init__(self,values:dict[str,bool]|None=None): self._values={str(k):bool(v) for k,v in (values or {}).items()}
    def enabled(self,name:str,default:bool=False)->bool: return self._values.get(name,default)
    def set(self,name:str,enabled:bool):
        if not name.strip(): raise ValueError("feature name cannot be empty")
        self._values[name]=bool(enabled)
    def snapshot(self)->dict[str,bool]: return dict(self._values)
