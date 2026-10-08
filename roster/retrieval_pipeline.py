"""Bounded retrieval pipeline producing ranked structured results."""
from roster.knowledge_search import search
from roster.retrieval_result import RetrievalResult

def retrieve(chunks,query,limit=5):
    return tuple(RetrievalResult(chunk.text,1.0/(index+1)) for index,chunk in enumerate(search(chunks,query,limit)))
