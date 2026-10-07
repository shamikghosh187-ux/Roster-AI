from roster.memory import ConversationMemory
from roster.models import Action, Intent
from roster.security import PermissionGate

class Agent:
    def __init__(self, provider, tools, memory=None, permissions=None):
        self.provider = provider
        self.tools = tools
        self.memory = memory or ConversationMemory()
        self.permissions = permissions or PermissionGate()

    def handle(self, user_text):
        self.memory.add("user", user_text)

        intent = self.provider.plan(user_text, self.memory.as_messages())
        if self.permissions.requires_confirmation(intent.action):
            if not self.permissions.request(intent):
                reply = "I didn't perform that action."
                self.memory.add("assistant", reply)
                return True, reply

        running, reply = self.tools.execute(intent, user_text, self.provider)
        if reply:
            self.memory.add("assistant", reply)
        return running, reply
