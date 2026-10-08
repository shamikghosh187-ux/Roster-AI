from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ToolInvocation:
    tool_name: str
    arguments: dict[str,Any]
    task_id: str | None = None
    request_id: str | None = None

    def normalized(self):
        return ToolInvocation(self.tool_name.strip(),dict(self.arguments),self.task_id,self.request_id)
