"""Conversation session state with bounded turn history."""
from dataclasses import dataclass
from collections import deque
@dataclass(frozen=True)
class SessionTurn: role:str; content:str
class Session:
    def __init__(self,session_id:str,max_turns:int=50):
        if not session_id: raise ValueError("session_id is required")
        if max_turns<1: raise ValueError("max_turns must be positive")
        self.session_id=session_id; self._turns=deque(maxlen=max_turns)
    def add(self,role:str,content:str):
        if not role or not content: raise ValueError("role and content are required")
        self._turns.append(SessionTurn(role,content))
    def turns(self): return list(self._turns)
