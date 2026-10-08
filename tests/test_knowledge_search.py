from roster.knowledge_search import search
from roster.knowledge_chunk import KnowledgeChunk

def test_search_returns_matching_chunks():
    chunks=[KnowledgeChunk("s",0,"python runtime"),KnowledgeChunk("s",1,"other")]; assert search(chunks,"python")[0].index==0
