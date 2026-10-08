"""Read intelligence limits from AdvancedSettings without exposing internals."""
def intelligence_limits(settings):
    return {"max_messages":settings.get("context.max_messages"),"max_chars":settings.get("context.max_chars"),"memory_enabled":settings.get("memory.enabled"),"retention_days":settings.get("memory.retention_days")}
