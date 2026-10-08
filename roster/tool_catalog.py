from roster.tool_contract import ToolContract

class ToolCatalog:
    def __init__(self): self._tools: dict[str,ToolContract]={}
    def upsert(self,tool):
        self._tools[tool.name.strip().lower()] = tool
        return tool

    def register(self,tool):
        key=tool.name.strip().lower()
        if key in self._tools: raise ValueError(f"tool already registered: {tool.name}")
        self._tools[key]=tool
        return tool
    def get(self,name): return self._tools.get(name.strip().lower())
    def names(self): return tuple(sorted(self._tools))
    def all(self): return tuple(self._tools.values())
