"""Health checks for the structured memory subsystem."""
def check(repository):
    try:
        records=repository.all(); return {"ok":True,"count":len(records)}
    except Exception as exc:
        return {"ok":False,"error":type(exc).__name__}
