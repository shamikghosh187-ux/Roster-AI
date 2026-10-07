from dataclasses import dataclass
from typing import Callable
from roster.models import Action, Intent

@dataclass(frozen=True)
class ToolSpec:
    action: Action
    description: str
    handler: Callable[[Intent, str, object | None], str]
    requires_confirmation: bool = False

class ToolRegistry:
    def __init__(self):
        self._tools: dict[Action, ToolSpec] = {}

    def register(self, spec: ToolSpec):
        self._tools[spec.action] = spec
        return self

    def get(self, action: Action) -> ToolSpec | None:
        return self._tools.get(action)

    def all(self) -> list[ToolSpec]:
        return list(self._tools.values())

    def descriptions(self) -> str:
        return "\n".join(
            f"- {spec.action.value}: {spec.description}"
            for spec in self._tools.values()
        )
