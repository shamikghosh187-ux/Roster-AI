"""Canonical memory categories used by retrieval and retention policies."""
from enum import Enum

class MemoryKind(str, Enum):
    FACT="fact"
    PREFERENCE="preference"
    GOAL="goal"
    PROFILE="profile"
    CONTEXT="context"
    TASK="task"
