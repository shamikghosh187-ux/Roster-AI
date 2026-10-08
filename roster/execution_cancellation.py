"""Cancellation boundary for production execution."""
from roster.cancel import CancelledError

def ensure_not_cancelled(token):
    if token is not None:
        token.raise_if_cancelled()

def cancellation_result(task_id, token):
    ensure_not_cancelled(token)
    return {"task_id": task_id, "status": "cancelled"}
