from roster.memory_filter import filter_records
from roster.memory_record import MemoryRecord

def test_filters_apply_kind_and_thresholds():
    records=[MemoryRecord("a","x",kind="goal",importance=.8),MemoryRecord("b","y",kind="fact",importance=.2)]
    assert [r.key for r in filter_records(records,kind="goal",min_importance=.5)]==["a"]
