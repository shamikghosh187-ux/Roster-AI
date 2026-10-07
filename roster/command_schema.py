"""Validated command envelope used between planner and tool layers."""
from dataclasses import dataclass,field
from typing import Any
@dataclass(frozen=True)
class Command:
    name:str
    arguments:dict[str,Any]=field(default_factory=dict)
    request_id:str|None=None
    def __post_init__(self):
        if not self.name or not self.name.strip(): raise ValueError("command name cannot be empty")
    def normalized(self):
        return Command(self.name.strip().upper(),dict(self.arguments),self.request_id)
