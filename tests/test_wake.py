from roster.wake import _matches_wake_word, _normalize


def test_wake_word_matching_is_case_and_punctuation_insensitive():
    assert _matches_wake_word("Hey, Roster!", "hey roster")
    assert _matches_wake_word("HEY ROSTER", "hey roster")


def test_wake_word_does_not_match_unrelated_speech():
    assert not _matches_wake_word("hello assistant", "hey roster")


def test_normalize_collapses_punctuation_and_whitespace():
    assert _normalize("  Hey,   Roster!! ") == "hey roster"
