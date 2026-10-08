import pytest
from roster.knowledge_chunk import KnowledgeChunk

def test_chunk_index_is_non_negative():
    assert KnowledgeChunk("s",0,"text").index==0
    with pytest.raises(ValueError): KnowledgeChunk("s",-1,"text")
