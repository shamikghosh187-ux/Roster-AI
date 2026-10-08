"""Explicit lifecycle operations for structured memory."""
from roster.memory_cleanup import expired_records

def cleanup(repository,retention_days,*,now=None):
    expired=expired_records(repository.all(),retention_days,now=now)
    for record in expired: repository.store.delete(record.key) if hasattr(repository,"store") else None
    return tuple(record.key for record in expired)
