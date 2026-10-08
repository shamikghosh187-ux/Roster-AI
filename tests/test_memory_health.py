from roster.memory_health import check
from roster.memory_repository import MemoryRepository

def test_memory_health_reports_repository_state(): assert check(MemoryRepository())=={"ok":True,"count":0}
