"""Deterministic scoring helpers for memory retrieval."""
def relevance(*, similarity: float, confidence: float, importance: float, recency: float=1.0) -> float:
    values=(similarity,confidence,importance,recency)
    if any(not 0 <= value <= 1 for value in values): raise ValueError("all scores must be between 0 and 1")
    return round(.45*similarity + .2*confidence + .2*importance + .15*recency, 6)
