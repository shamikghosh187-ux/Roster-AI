from roster.memory_record import MemoryRecord
from roster.memory_query import MemoryQuery
from roster.memory_ranker import rank

def test_ranker_prioritizes_matching_memory():
    records=[MemoryRecord("language","Python",importance=.8),MemoryRecord("editor","Vim")]
    result=rank(records,MemoryQuery("Python"))
    assert result and result[0][1].key=="language"
