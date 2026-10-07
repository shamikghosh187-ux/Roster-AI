from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class Action(str, Enum):
    CHAT = "chat"
    EXIT = "exit"
    OPEN_APP = "open_app"
    SEARCH = "search"
    YOUTUBE = "youtube"
    WHATSAPP = "whatsapp"
    SCREEN_VISION = "screen_vision"

@dataclass
class ConversationTurn:
    role: str
    content: str

@dataclass
class Intent:
    action: Action
    argument: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
