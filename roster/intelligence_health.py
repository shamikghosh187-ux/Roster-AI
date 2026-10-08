"""Composite health report for intelligence subsystems."""
def report(memory_gateway,settings):
    return {"memory_enabled":settings.get("memory.enabled"),"memory":memory_gateway is not None}
