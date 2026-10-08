"""Small unit of executable agent work."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Subtask:
    id: str
    description: str
    depends_on: tuple[str,...] = ()
