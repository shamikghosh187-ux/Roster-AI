"""Chronological view of memory records."""
def timeline(records):
    return tuple(sorted(records,key=lambda record:record.created_at))
