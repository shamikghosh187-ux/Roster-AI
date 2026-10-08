"""Barge-in controller: user speech can interrupt Roster speech."""
from __future__ import annotations
from roster.cancel import CancellationToken

class BargeInController:
    def __init__(self,runtime,*,threshold=.03,consecutive_frames=2):
        if threshold<=0 or consecutive_frames<1: raise ValueError("invalid barge-in configuration")
        self.runtime=runtime; self.threshold=threshold; self.consecutive_frames=consecutive_frames; self._count=0
    def feed_rms(self,rms):
        if rms>=self.threshold:self._count+=1
        else:self._count=0
        if self._count>=self.consecutive_frames:
            self._count=0
            self.runtime.stop_speaking()
            return True
        return False
