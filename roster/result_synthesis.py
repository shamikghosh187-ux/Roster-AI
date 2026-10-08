"""Deterministic synthesis boundary for tool results."""
def summarize(results,limit=5):
    if limit<1: raise ValueError("limit must be positive")
    return tuple(str(result) for result in results[-limit:])
