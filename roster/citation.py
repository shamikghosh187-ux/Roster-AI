"""Stable citation object for retrieved knowledge."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Citation:
    source_id: str
    chunk_index: int
    label: str
