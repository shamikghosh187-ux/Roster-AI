"""Bounded in-memory TTL cache."""
from time import monotonic
from threading import Lock
class TTLCache:
    def __init__(self,max_size:int=256,ttl_seconds:float=300):
        if max_size<1 or ttl_seconds<=0: raise ValueError("invalid cache configuration")
        self.max_size=max_size; self.ttl_seconds=ttl_seconds; self._items={}; self._lock=Lock()
    def set(self,key,value):
        with self._lock:
            if key in self._items: self._items.pop(key)
            elif len(self._items)>=self.max_size: self._items.pop(next(iter(self._items)))
            self._items[key]=(monotonic()+self.ttl_seconds,value)
    def get(self,key,default=None):
        with self._lock:
            item=self._items.get(key)
            if item is None: return default
            expires,value=item
            if expires<=monotonic(): self._items.pop(key,None); return default
            return value
    def clear(self):
        with self._lock: self._items.clear()
