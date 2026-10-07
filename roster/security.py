from roster.tools.registry import ToolRegistry

class PermissionGate:
    def __init__(self, enabled=True, callback=None):
        self.enabled=enabled
        self.callback=callback

    def requires_confirmation(self, action, registry=None):
        if not self.enabled: return False
        spec=registry.get(action) if registry else None
        return bool(spec and spec.requires_confirmation)

    def request(self, intent):
        if self.callback:
            return bool(self.callback(intent))
        target=intent.argument or intent.action.value
        answer=input(f"Roster wants to execute {intent.action.value} ({target}). Allow? [y/N] ").strip().lower()
        return answer in {"y","yes"}
