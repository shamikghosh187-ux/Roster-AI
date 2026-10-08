"""Metadata for a retrievable knowledge source."""
from dataclasses import dataclass

@dataclass(frozen=True)
class KnowledgeSource:
    id: str
    title: str
    location: str
    kind: str = "file"
