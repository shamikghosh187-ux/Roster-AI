"""Canonical memory categories used by retrieval and retention policies."""
from enum import StrEnum

class MemoryKind(StrEnum):
    FACT="fact"
    PREFERENCE="preference"
    GOAL="goal"
    PROFILE="profile"
    CONTEXT="context"
    TASK="task"
