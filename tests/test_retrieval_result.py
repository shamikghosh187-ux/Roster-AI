import pytest
from roster.retrieval_result import RetrievalResult

def test_retrieval_result_validates_score():
    assert RetrievalResult("text",.8).score==.8
    with pytest.raises(ValueError): RetrievalResult("text",2)
