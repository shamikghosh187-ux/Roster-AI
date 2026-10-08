from roster.models import Action
from roster.tools.registry import ToolRegistry, ToolSpec
from roster.registry_adapter import catalog_from_registry

def test_registry_adapter_exposes_existing_tools():
    registry=ToolRegistry(); registry.register(ToolSpec(Action.CHAT,"chat",lambda intent,user,provider:"ok"))
    catalog=catalog_from_registry(registry)
    assert catalog.get("chat").description=="chat"


def test_registry_adapter_preserves_intent_and_context():
    from roster.models import Intent
    seen={}
    def handler(intent, raw, context):
        seen.update(intent=intent, raw=raw, context=context); return intent.argument
    registry=ToolRegistry().register(ToolSpec(Action.SEARCH,"search",handler))
    tool=catalog_from_registry(registry).get("search")
    result=tool.handler({"argument":"python","query":"docs"},{"raw_input":"find python docs","tool_context":{"source":"test"}})
    assert result=="python"
    assert isinstance(seen["intent"],Intent)
    assert seen["intent"].action is Action.SEARCH
    assert seen["intent"].metadata["query"]=="docs"
    assert seen["raw"]=="find python docs"
    assert seen["context"]=={"source":"test"}
