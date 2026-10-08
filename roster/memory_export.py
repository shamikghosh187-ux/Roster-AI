"""Portable, value-preserving memory export format."""
from roster.memory_serializer import dumps

def export_records(records):
    return "\n".join(dumps(record) for record in records)+"\n"
