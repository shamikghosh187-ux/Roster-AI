from dataclasses import dataclass
from enum import Enum

class ConfirmationMode(str,Enum):
    ALWAYS="always"; SMART="smart"; NEVER="never"
@dataclass(frozen=True)
class ExecutionPolicy:
    confirmation: ConfirmationMode=ConfirmationMode.SMART
    max_parallel: int=4
    timeout_seconds: float=60.0
    def __post_init__(self):
        if self.max_parallel<1: raise ValueError("max_parallel must be positive")
        if self.timeout_seconds<=0: raise ValueError("timeout_seconds must be positive")
