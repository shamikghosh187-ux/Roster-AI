from copy import deepcopy
from dataclasses import dataclass,field
from typing import Any,Callable

@dataclass(frozen=True)
class ToolContract:
    name:str
    description:str
    version:str="1.0"
    input_schema:dict[str,Any]=field(default_factory=dict)
    sensitive:bool=False
    handler:Callable[...,Any]|None=None

    def __post_init__(self):
        if not isinstance(self.name,str) or not self.name.strip(): raise ValueError("tool name cannot be empty")
        if not isinstance(self.version,str) or not self.version.strip(): raise ValueError("tool version cannot be empty")
        if not isinstance(self.input_schema,dict): raise TypeError("input_schema must be a dictionary")
        object.__setattr__(self,"input_schema",deepcopy(self.input_schema))
