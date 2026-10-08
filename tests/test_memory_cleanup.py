from datetime import datetime,timezone,timedelta
from roster.memory_record import MemoryRecord
from roster.memory_cleanup import expired_records

def test_cleanup_selects_only_expired_records():
    now=datetime.now(timezone.utc); old=MemoryRecord("old","x",created_at=(now-timedelta(days=20)).isoformat()); fresh=MemoryRecord("fresh","x",created_at=now.isoformat())
    assert [r.key for r in expired_records([old,fresh],7,now=now)]==["old"]
