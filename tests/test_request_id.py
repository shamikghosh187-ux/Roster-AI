from roster.request_id import get_request_id, new_request_id, set_request_id

def test_request_id_lifecycle():
    set_request_id(None)
    first = new_request_id()
    assert first
    assert get_request_id() == first
    second = new_request_id()
    assert second != first
    assert get_request_id() == second
