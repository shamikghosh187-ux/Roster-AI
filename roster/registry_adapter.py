from roster.models import Intent
from roster.tool_catalog import ToolCatalog
from roster.tool_contract import ToolContract

def catalog_from_registry(registry):
    catalog=ToolCatalog()
    for spec in registry.all():
        def invoke(args, ctx, spec=spec):
            context=ctx if isinstance(ctx, dict) else {}
            argument=args.get("argument", context.get("argument", ""))
            metadata=dict(context.get("metadata", {}))
            metadata.update({k:v for k,v in args.items() if k != "argument"})
            intent=Intent(action=spec.action, argument=argument, metadata=metadata)
            return spec.handler(intent, context.get("raw_input", ""), context.get("tool_context"))
        catalog.register(ToolContract(
            name=spec.action.value,
            description=spec.description,
            input_schema={"type":"object"},
            sensitive=spec.requires_confirmation,
            retry_safe=spec.retry_safe,
            handler=invoke,
        ))
    return catalog
