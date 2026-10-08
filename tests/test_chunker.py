from roster.chunker import chunk

def test_chunker_splits_text_into_addressable_windows():
    result=chunk("s","abcdefgh",3); assert [c.text for c in result]==["abc","def","gh"]
