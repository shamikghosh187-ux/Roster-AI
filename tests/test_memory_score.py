from roster.memory_score import relevance

def test_relevance_weights_are_bounded_and_deterministic():
    assert relevance(similarity=1,confidence=1,importance=1,recency=1)==1
    assert relevance(similarity=0,confidence=0,importance=0,recency=0)==0
