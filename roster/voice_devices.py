"""Audio device abstraction for realtime voice sessions."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class AudioDevice:
    index:int|None
    name:str
    input_channels:int
    output_channels:int
    sample_rate:float

class AudioDeviceManager:
    def __init__(self, backend=None):
        self.backend=backend
    def list_devices(self):
        if self.backend is None or not hasattr(self.backend,"query_devices"): return []
        out=[]
        for i,d in enumerate(self.backend.query_devices()):
            out.append(AudioDevice(i,str(d.get("name","")),int(d.get("max_input_channels",0)),int(d.get("max_output_channels",0)),float(d.get("default_samplerate",0))))
        return out
    def inputs(self):
        return [d for d in self.list_devices() if d.input_channels>0]
    def outputs(self):
        return [d for d in self.list_devices() if d.output_channels>0]
    def validate(self,index,*,input_device=True):
        if index is None:return True
        for d in self.list_devices():
            if d.index==index:
                return d.input_channels>0 if input_device else d.output_channels>0
        return False
