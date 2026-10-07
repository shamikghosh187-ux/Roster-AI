from roster.session import Session
def test_session_bounds_turn_history():
    s=Session("s1",2); s.add("user","one"); s.add("assistant","two"); s.add("user","three")
    assert [t.content for t in s.turns()]==["two","three"]
