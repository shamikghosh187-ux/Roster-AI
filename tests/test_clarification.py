from roster.clarification import assess

def test_clarification_flags_underspecified_requests(): assert assess("").needed; assert assess("open").needed; assert not assess("hello").needed
