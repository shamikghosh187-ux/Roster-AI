from roster.intent import Intent

def test_intent_validates_confidence():
    assert Intent("chat",.9).name=="chat"
    try: Intent("chat",1.1)
    except ValueError: pass
    else: raise AssertionError("expected validation error")
