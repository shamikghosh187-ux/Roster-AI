"""Local keyword retrieval over knowledge chunks."""
from roster.knowledge_chunk import KnowledgeChunk

def search(chunks,query,limit=5):
    q=query.strip().lower()
    if not q:return ()
    matches=[c for c in chunks if q in c.text.lower()]
    return tuple(matches[:limit])
