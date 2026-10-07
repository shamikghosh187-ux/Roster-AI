from roster.event_log import EventJournal
def test_event_journal_bounds_history():
    j=EventJournal(2); j.append("first"); j.append("second",value=2); j.append("third")
    events=j.snapshot(); assert [e.name for e in events]==["second","third"]; assert events[0].payload["value"]==2
