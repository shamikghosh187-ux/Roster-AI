from roster.tool_catalog import ToolCatalog
from roster.tool_contract import ToolContract


def catalog_from_registry(registry):
    catalog=ToolCatalog()
    for spec in registry.all():
        catalog.register(ToolContract(name=spec.action.value,description=spec.description,sensitive=spec.requires_confirmation,handler=lambda args,ctx,spec=spec: spec.handler(type("Intent",(),{"argument":args.get("argument","")})(),"",None)))
    return catalog
