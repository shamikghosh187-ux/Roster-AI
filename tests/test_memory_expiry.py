from datetime import datetime,timezone,timedelta
from roster.memory_expiry import is_expired

def test_expiry_uses_retention_window():
    now=datetime.now(timezone.utc); old=(now-timedelta(days=10)).isoformat()
    assert is_expired(old,7,now=now); assert not is_expired(old,30,now=now)
