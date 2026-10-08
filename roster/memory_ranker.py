"""Simple explainable ranking over structured memories."""
from roster.memory_record import MemoryRecord
from roster.memory_query import MemoryQuery
from roster.memory_score import relevance
from roster.memory_dedupe import normalize_text

def rank(records: list[MemoryRecord]|tuple[MemoryRecord,...], query: MemoryQuery):
    q=normalize_text(query.text)
    scored=[]
    for record in records:
        if query.kind and record.kind != query.kind: continue
        text=normalize_text(record.key+" "+record.value)
        similarity=1.0 if q and q in text else (0.5 if q and any(part in text for part in q.split()) else 0.0)
        score=relevance(similarity=similarity,confidence=record.confidence,importance=record.importance)
        if score >= query.minimum_score: scored.append((score,record))
    scored.sort(key=lambda item:(-item[0],item[1].key))
    return scored[:query.limit]
