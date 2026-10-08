from roster.memory_record import MemoryRecord
from roster.memory_stats import summarize

def test_memory_stats_do_not_expose_values():
    result=summarize([MemoryRecord("secret","hidden"),MemoryRecord("goal","learn",kind="goal")]); assert result["count"]==2; assert "hidden" not in str(result)
