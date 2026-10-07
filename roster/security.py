from roster.models import Action
from roster.tools.registry import ToolRegistry

class PermissionGate:
    def __init__(self, enabled=True):
        self.enabled = enabled

    def requires_confirmation(self, action, registry: ToolRegistry | None = None):
        if not self.enabled:
            return False
        if registry:
            spec = registry.get(action)
            return bool(spec and spec.requires_confirmation)
        return action in {Action.OPEN_APP, Action.WHATSAPP}

    def request(self, intent):
        target = intent.argument or intent.action.value
        answer = input(f"Roster wants to {intent.action.value} ({target}). Allow? [y/N] ").strip().lower()
        return answer in {"y", "yes"}
