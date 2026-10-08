from roster.result_synthesis import summarize

def test_synthesis_bounds_result_history(): assert summarize([1,2,3],2)==("2","3")
