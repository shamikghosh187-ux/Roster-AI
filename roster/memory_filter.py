"""Composable filters for memory retrieval."""
def filter_records(records,*,kind=None,min_confidence=0.0,min_importance=0.0):
    if not 0 <= min_confidence <= 1 or not 0 <= min_importance <= 1: raise ValueError("thresholds must be between 0 and 1")
    return tuple(r for r in records if (kind is None or r.kind==kind) and r.confidence>=min_confidence and r.importance>=min_importance)
