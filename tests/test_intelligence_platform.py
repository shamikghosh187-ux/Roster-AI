from roster.intelligence_platform import IntelligencePlatform
from roster.memory_gateway import MemoryGateway
from roster.memory_repository import MemoryRepository
from roster.memory_record import MemoryRecord

def test_platform_composes_intent_planning_and_memory():
    memory=MemoryGateway(MemoryRepository()); memory.remember(MemoryRecord("language","Python"))
    platform=IntelligencePlatform(memory); assert platform.inspect("hello").name=="chat"; assert platform.plan("learn").goal=="learn"
