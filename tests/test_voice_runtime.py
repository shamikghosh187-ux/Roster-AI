from roster.voice_settings import VoiceSettings, VoiceMode
from roster.voice_vad import VoiceActivityDetector
from roster.voice_runtime import VoiceRuntime

def test_voice_settings_reject_unsafe_values():
    try: VoiceSettings(tts_volume=2)
    except ValueError: pass
    else: assert False

def test_vad_requires_consecutive_speech():
    v=VoiceActivityDetector(start_threshold=.1,end_threshold=.05,min_speech_frames=2,end_silence_frames=2)
    assert not v.process([.11,.11]).started
    assert v.process([.11,.11]).started

def test_vad_ends_after_silence():
    v=VoiceActivityDetector(start_threshold=.1,end_threshold=.05,min_speech_frames=1,end_silence_frames=2)
    assert v.process([.2,.2]).started
    assert not v.process([.01,.01]).ended
    assert v.process([.01,.01]).ended

class FakeTTS:
    def __init__(self): self.calls=[]; self.stopped=0
    def say(self,text): self.calls.append(("say",text))
    def runAndWait(self): self.calls.append(("wait",))
    def stop(self): self.stopped+=1
    def setProperty(self,k,v): self.calls.append(("property",k,v))

def test_tts_is_interruptible():
    t=FakeTTS(); r=VoiceRuntime(VoiceSettings(),tts=t)
    r.apply_tts_settings(); assert r.speak("hello")
    r.stop_speaking()
    assert t.stopped >= 1

def test_disabled_voice_does_not_capture():
    r=VoiceRuntime(VoiceSettings(enabled=False),audio=object())
    assert r.capture()==[]

def test_mode_is_explicit():
    assert VoiceSettings(mode=VoiceMode.CONTINUOUS).mode is VoiceMode.CONTINUOUS
