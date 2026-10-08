from roster.memory_gateway import MemoryGateway
from roster.memory_record import MemoryRecord
from roster.memory_query import MemoryQuery
from roster.memory_repository import MemoryRepository

def test_gateway_combines_write_and_ranked_recall():
    gateway=MemoryGateway(MemoryRepository()); gateway.remember(MemoryRecord("language","Python")); assert gateway.recall(MemoryQuery("Python"))[0][1].value=="Python"
