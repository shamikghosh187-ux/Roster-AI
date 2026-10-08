from roster.knowledge_source import KnowledgeSource

def test_knowledge_source_preserves_location(): assert KnowledgeSource("1","README","README.md").location=="README.md"
