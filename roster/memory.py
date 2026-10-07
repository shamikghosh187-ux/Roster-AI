from collections import deque
from roster.models import ConversationTurn

class ConversationMemory:
    def __init__(self, max_turns=20):
        self.turns = deque(maxlen=max_turns)

    def add(self, role, content):
        self.turns.append(ConversationTurn(role=role, content=content))

    def recent(self):
        return list(self.turns)

    def as_messages(self):
        return [{"role": t.role, "content": t.content} for t in self.turns]

    def clear(self):
        self.turns.clear()
