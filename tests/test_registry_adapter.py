from roster.models import Action
from roster.tools.registry import ToolRegistry, ToolSpec
from roster.registry_adapter import catalog_from_registry

def test_registry_adapter_exposes_existing_tools():
    registry=ToolRegistry(); registry.register(ToolSpec(Action.CHAT,"chat",lambda intent,user,provider:"ok"))
    catalog=catalog_from_registry(registry)
    assert catalog.get("chat").description=="chat"
