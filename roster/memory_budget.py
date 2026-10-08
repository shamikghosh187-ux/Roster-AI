"""Bound retrieval results by item and character budgets."""
def within_budget(records,max_items=10,max_chars=4000):
    if max_items<1 or max_chars<1: raise ValueError("budgets must be positive")
    selected=[]; used=0
    for record in records:
        size=len(record.key)+len(record.value)
        if len(selected)>=max_items or used+size>max_chars: break
        selected.append(record); used+=size
    return tuple(selected)
