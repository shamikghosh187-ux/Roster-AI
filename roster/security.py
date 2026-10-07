from roster.models import Action

# Actions that can cause an external side effect.
CONFIRM_ACTIONS = {
    Action.OPEN_APP,
    Action.WHATSAPP,
}

class PermissionGate:
    def __init__(self, enabled=True):
        self.enabled = enabled

    def requires_confirmation(self, action):
        return self.enabled and action in CONFIRM_ACTIONS

    def request(self, intent):
        target = intent.argument or intent.action.value
        answer = input(f"Roster wants to {intent.action.value} ({target}). Allow? [y/N] ").strip().lower()
        return answer in {"y", "yes"}
