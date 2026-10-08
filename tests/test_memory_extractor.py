from roster.memory_extractor import extract_explicit_preference

def test_extractor_only_captures_explicit_preference_language():
    result=extract_explicit_preference("I prefer concise answers."); assert result and result.value=="concise answers"
    assert extract_explicit_preference("Maybe concise answers.") is None
