"""Validated line-oriented memory import."""
from roster.memory_serializer import loads

def import_records(payload):
    records=[]
    for line in payload.splitlines():
        if line.strip(): records.append(loads(line))
    return tuple(records)
