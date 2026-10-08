"""Public composition boundary for Roster intelligence primitives."""
from roster.intent_classifier import IntentClassifier
from roster.memory_gateway import MemoryGateway
from roster.plan_builder import build

class IntelligencePlatform:
    def __init__(self,memory): self.classifier=IntentClassifier(); self.memory=memory
    def inspect(self,text): return self.classifier.classify(text)
    def plan(self,goal): return build(goal)
    def recall(self,query): return self.memory.recall(query)
