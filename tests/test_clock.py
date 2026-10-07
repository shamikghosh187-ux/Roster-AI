from datetime import datetime, timezone
from roster.clock import unix_time, utc_now, utc_timestamp

def test_clock_returns_utc_values():
    now = utc_now()
    assert now.tzinfo == timezone.utc
    assert utc_timestamp().endswith("+00:00")
    assert unix_time() > 0
