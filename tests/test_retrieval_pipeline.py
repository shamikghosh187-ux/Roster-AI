from roster.knowledge_chunk import KnowledgeChunk
from roster.retrieval_pipeline import retrieve

def test_pipeline_returns_structured_ranked_results():
    result=retrieve([KnowledgeChunk("s",0,"python"),KnowledgeChunk("s",1,"python tips")],"python"); assert result[0].score==1
