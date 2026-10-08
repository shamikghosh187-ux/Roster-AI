"""Route classified intents to stable execution categories."""
from roster.intent import Intent

def route(intent: Intent) -> str:
    if intent.name=="exit": return "lifecycle"
    if intent.name=="tool": return "tool"
    return "conversation"
