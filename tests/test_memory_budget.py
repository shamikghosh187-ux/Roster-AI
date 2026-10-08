from roster.memory_budget import within_budget
from roster.memory_record import MemoryRecord

def test_budget_limits_items_and_characters():
    records=[MemoryRecord("a","123"),MemoryRecord("b","456")]; assert len(within_budget(records,max_items=1))==1
