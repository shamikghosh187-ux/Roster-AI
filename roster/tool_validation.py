class ToolValidationError(ValueError): pass

def validate_arguments(schema,arguments):
    arguments=dict(arguments)
    required=tuple(schema.get("required",()))
    missing=[name for name in required if name not in arguments]
    if missing: raise ToolValidationError("missing required arguments: "+", ".join(sorted(missing)))
    allowed=schema.get("properties")
    if allowed is not None:
        unknown=set(arguments)-set(allowed)
        if unknown: raise ToolValidationError("unknown arguments: "+", ".join(sorted(unknown)))
    return arguments
