from roster.memory_dedupe import duplicate_key

def test_duplicate_key_normalizes_case_and_whitespace():
    assert duplicate_key(" Name ","  Roster   AI ")=="name::roster ai"
