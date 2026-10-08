"""Deterministic baseline intent classifier for agent routing."""
from roster.intent import Intent

class IntentClassifier:
    def classify(self,text):
        value=(text or "").strip().lower()
        if not value: return Intent("empty",1.0)
        if value in {"exit","quit","stop"}: return Intent("exit",.99)
        if value.startswith(("open ","search ","find ","play ")): return Intent("tool",.8,value)
        return Intent("chat",.65,value)
