"""Request correlation identifiers for runtime operations."""
from contextvars import ContextVar
from uuid import uuid4

_request_id = ContextVar("roster_request_id", default=None)

def new_request_id() -> str:
    value = uuid4().hex
    _request_id.set(value)
    return value

def get_request_id() -> str | None:
    return _request_id.get()

def set_request_id(value: str | None) -> None:
    _request_id.set(value)
