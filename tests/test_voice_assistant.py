from roster.voice_assistant import VoiceAssistantBridge, VoiceTurn
from roster.voice_runtime import VoiceRuntime
from roster.voice_settings import VoiceSettings

class FakeAgent:
    def handle(self,text,cancellation=None): return True,"Done"

class FakeRuntime(VoiceRuntime):
    def capture(self,**kwargs): return [[.1,.1]]
    def speak(self,text,**kwargs): return True

def test_voice_bridge_routes_transcript_to_agent():
    seen=[]
    bridge=VoiceAssistantBridge(FakeAgent(),FakeRuntime(VoiceSettings()),transcribe=lambda f:(seen.append(f) or "open app"))
    turn=bridge.handle_audio()
    assert isinstance(turn,VoiceTurn)
    assert turn.status=="completed" and turn.response=="Done"
    assert seen

def test_empty_transcript_does_not_call_agent():
    class Agent:
        def handle(self,*a,**k): raise AssertionError
    turn=VoiceAssistantBridge(Agent(),FakeRuntime(VoiceSettings()),transcribe=lambda f:"").handle_audio()
    assert turn.status=="no_speech"
