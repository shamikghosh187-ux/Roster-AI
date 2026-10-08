import pytest
from roster.memory import ConversationMemory

def test_conversation_memory_rejects_invalid_capacity():
    with pytest.raises(ValueError): ConversationMemory(0)

def test_conversation_memory_rejects_invalid_turns():
    memory=ConversationMemory()
    with pytest.raises(ValueError): memory.add("","hello")
    with pytest.raises(TypeError): memory.add("user",123)

def test_conversation_memory_keeps_recent_turns():
    memory=ConversationMemory(2)
    memory.add("user","one"); memory.add("assistant","two"); memory.add("user","three")
    assert [item.content for item in memory.recent()]==["two","three"]
