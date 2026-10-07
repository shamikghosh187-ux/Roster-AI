from dataclasses import dataclass
@dataclass
class PluginTool:
    name:str; description:str; handler:object; requires_confirmation:bool=True
class PluginRegistry:
    def __init__(self): self.tools={}
    def register(self,tool): self.tools[tool.name]=tool
    def describe(self): return [{'name':t.name,'description':t.description,'requires_confirmation':t.requires_confirmation} for t in self.tools.values()]
    def call(self,name,args=None): return self.tools[name].handler(args or {})
