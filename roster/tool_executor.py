from roster.tool_result import ToolResult
from roster.tool_validation import validate_arguments

class ToolExecutor:
    def __init__(self,catalog,enablement=None):
        self.catalog=catalog
        self.enablement=enablement
    def execute(self,name,arguments,context=None):
        tool=self.catalog.get(name)
        if tool is None: return ToolResult.failure(f"unknown tool: {name}")
        if self.enablement is not None and not self.enablement.is_enabled(tool.name):
            return ToolResult.failure(f"tool disabled: {tool.name}")
        try:
            args=validate_arguments(tool.input_schema,arguments)
            if tool.handler is None: return ToolResult.failure(f"tool has no handler: {tool.name}")
            return ToolResult.success(tool.handler(args,context))
        except Exception as exc:
            return ToolResult.failure(str(exc))
