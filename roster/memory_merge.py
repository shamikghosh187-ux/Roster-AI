"""Merge candidate memories with conflict resolution and deduplication."""
from roster.memory_conflict import detect_conflict
from roster.memory_resolver import resolve
from roster.memory_dedupe import duplicate_key

def merge(existing,candidate):
    if duplicate_key(existing.key,existing.value)==duplicate_key(candidate.key,candidate.value): return existing
    conflict=detect_conflict(existing,candidate)
    return resolve(conflict) if conflict else candidate
