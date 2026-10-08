"""Pure cleanup selection for expired memories."""
from roster.memory_record import MemoryRecord
from roster.memory_expiry import is_expired

def expired_records(records,retention_days,*,now=None):
    return tuple(r for r in records if is_expired(r.created_at,retention_days,now=now))
