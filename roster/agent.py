from roster.memory import ConversationMemory
from roster.models import Action
from roster.security import PermissionGate

class Agent:
    def __init__(self, provider, tools, memory=None, permissions=None, max_steps=5):
        self.provider = provider
        self.tools = tools
        self.memory = memory or ConversationMemory()
        self.permissions = permissions or PermissionGate()
        self.max_steps = max_steps

    def handle(self, user_text):
        self.memory.add("user", user_text)
        current_request = user_text

        for step in range(self.max_steps):
            intent = self.provider.plan(
                current_request,
                self.memory.as_messages(),
                tool_descriptions=self.tools.registry.descriptions(),
            )

            if self.permissions.requires_confirmation(intent.action, self.tools.registry):
                if not self.permissions.request(intent):
                    reply = "I didn't perform that action."
                    self.memory.add("assistant", reply)
                    return True, reply

            running, result = self.tools.execute(intent, user_text, self.provider)

            if intent.action in {Action.CHAT, Action.EXIT}:
                self.memory.add("assistant", result)
                return running, result

            self.memory.add("assistant", f"[tool:{intent.action.value}] {result}")

            if not running:
                return running, result

            if step == self.max_steps - 1:
                reply = "I reached the execution limit before finishing the task."
                self.memory.add("assistant", reply)
                return True, reply

            current_request = (
                "Continue the user's task from the latest tool result. "
                "If the task is complete, use chat and give a concise final answer. "
                f"Latest tool result: {result}"
            )

        return True, "I couldn't complete that request."
