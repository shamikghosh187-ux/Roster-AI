"""Privacy-safe memory statistics."""
def summarize(records):
    records=tuple(records)
    by_kind={}
    for record in records: by_kind[record.kind]=by_kind.get(record.kind,0)+1
    return {"count":len(records),"by_kind":dict(sorted(by_kind.items()))}
