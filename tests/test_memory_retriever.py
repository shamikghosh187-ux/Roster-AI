from roster.memory_gateway import MemoryGateway
from roster.memory_repository import MemoryRepository
from roster.memory_record import MemoryRecord
from roster.memory_retriever import retrieve

def test_retriever_returns_matching_memory():
    gateway=MemoryGateway(MemoryRepository()); gateway.remember(MemoryRecord("language","Python")); assert retrieve(gateway,"Python")[0][1].value=="Python"
