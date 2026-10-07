from collections import deque

from roster.models import ConversationTurn


class ConversationMemory:
    def __init__(self, max_turns=20, store=None):
        self.turns = deque(maxlen=max_turns)
        self.store = store

        if self.store:
            for turn in self.store.recent(max_turns):
                self.turns.append(turn)

    def add(self, role, content):
        turn = ConversationTurn(role=role, content=content)
        self.turns.append(turn)
        if self.store:
            self.store.add(role, content)

    def recent(self):
        return list(self.turns)

    def as_messages(self):
        return [{"role": t.role, "content": t.content} for t in self.turns]

    def clear(self):
        self.turns.clear()
        if self.store:
            self.store.clear()
