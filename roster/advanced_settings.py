"""Advanced, typed, persistent runtime settings for Roster."""
from __future__ import annotations
import json,os,tempfile
from dataclasses import dataclass
from threading import RLock
from pathlib import Path
from typing import Any,Callable

@dataclass(frozen=True)
class SettingSpec:
    key:str
    default:Any
    kind:type
    description:str
    restart_required:bool=False
    minimum:float|None=None
    maximum:float|None=None
    choices:tuple[Any,...]=()

SPECS=(
    SettingSpec("profile","default",str,"Active settings profile."),
    SettingSpec("privacy.mode","standard",str,"Privacy mode.",choices=("standard","private","strict")),
    SettingSpec("privacy.telemetry",False,bool,"Allow non-secret local telemetry."),
    SettingSpec("memory.enabled",True,bool,"Enable conversational memory."),
    SettingSpec("memory.retention_days",90,int,"Maximum retained memory age.",minimum=0,maximum=3650),
    SettingSpec("voice.enabled",True,bool,"Enable voice input/output."),
    SettingSpec("voice.interruptible",True,bool,"Allow speech output to be interrupted."),
    SettingSpec("wake.enabled",True,bool,"Enable wake-word detection."),
    SettingSpec("wake.sensitivity",0.65,float,"Wake detector sensitivity.",minimum=0.0,maximum=1.0),
    SettingSpec("assistant.autonomy","balanced",str,"Action autonomy.",choices=("cautious","balanced","autonomous")),
    SettingSpec("assistant.confirmation","smart",str,"Tool confirmation.",choices=("always","smart","never")),
    SettingSpec("assistant.max_parallel_tasks",2,int,"Maximum concurrent background tasks.",minimum=1,maximum=16),
    SettingSpec("assistant.tool_timeout_seconds",30.0,float,"Default tool execution timeout.",minimum=1.0,maximum=600.0),
    SettingSpec("context.max_messages",24,int,"Maximum conversational messages in context.",minimum=1,maximum=200),
    SettingSpec("context.max_chars",24000,int,"Maximum context characters.",minimum=1000,maximum=500000),
    SettingSpec("performance.cache_enabled",True,bool,"Enable safe local caching."),
    SettingSpec("performance.max_retries",2,int,"Provider retry count.",minimum=0,maximum=8),
    SettingSpec("ui.response_style","natural",str,"Response style.",choices=("concise","natural","detailed")),
)
class SettingsError(ValueError): pass

def _spec_map(): return {spec.key:spec for spec in SPECS}

def _coerce(spec,value):
    if spec.kind is bool:
        if isinstance(value,bool): result=value
        elif isinstance(value,str) and value.strip().lower() in {"true","1","yes","on"}: result=True
        elif isinstance(value,str) and value.strip().lower() in {"false","0","no","off"}: result=False
        else: raise SettingsError(f"{spec.key} must be a boolean")
    elif spec.kind is int:
        if isinstance(value,bool): raise SettingsError(f"{spec.key} must be an integer")
        try: result=int(value)
        except (TypeError,ValueError) as exc: raise SettingsError(f"{spec.key} must be an integer") from exc
    elif spec.kind is float:
        try: result=float(value)
        except (TypeError,ValueError) as exc: raise SettingsError(f"{spec.key} must be a number") from exc
    elif spec.kind is str: result=str(value)
    else: raise SettingsError(f"unsupported setting type for {spec.key}")
    if spec.minimum is not None and result<spec.minimum: raise SettingsError(f"{spec.key} must be >= {spec.minimum}")
    if spec.maximum is not None and result>spec.maximum: raise SettingsError(f"{spec.key} must be <= {spec.maximum}")
    if spec.choices and result not in spec.choices: raise SettingsError(f"{spec.key} must be one of: {', '.join(map(str,spec.choices))}")
    return result

class AdvancedSettings:
    def __init__(self,path=None):
        self.path=Path(path or Path.home()/".roster"/"settings.json").expanduser()
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self._callbacks=[]; self._lock=RLock(); self._data=self._load()
    def _load(self):
        if not self.path.exists(): return {}
        try: raw=json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError,ValueError): return {}
        return raw if isinstance(raw,dict) else {}
    def _save(self):
        payload=json.dumps(self._data,ensure_ascii=False,indent=2,sort_keys=True)
        fd,temporary=tempfile.mkstemp(prefix=".settings-",suffix=".tmp",dir=self.path.parent)
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as handle:
                handle.write(payload); handle.flush(); os.fsync(handle.fileno())
            os.replace(temporary,self.path)
        finally:
            if os.path.exists(temporary): os.unlink(temporary)
    def get(self,key,default=None):
        spec=_spec_map().get(key)
        if spec is None: raise SettingsError(f"unknown setting: {key}")
        with self._lock:return self._data.get(key,spec.default if default is None else default)
    def set(self,key,value):
        with self._lock:
            return self._set_locked(key,value)
    def _set_locked(self,key,value):
        spec=_spec_map().get(key)
        if spec is None: raise SettingsError(f"unknown setting: {key}")
        normalized=_coerce(spec,value); previous=self.get(key)
        if previous==normalized:return normalized
        self._data[key]=normalized; self._save()
        for callback in tuple(self._callbacks): callback(key,previous,normalized)
        return normalized
    def update(self,values):
        with self._lock:
            normalized={key:_coerce(_spec_map().get(key) or self._unknown(key),value) for key,value in values.items()}
            previous={key:self._data.get(key,_spec_map()[key].default) for key in normalized}
            changed={key:value for key,value in normalized.items() if previous[key]!=value}
            if not changed:return normalized
            self._data.update(changed); self._save()
            callbacks=tuple(self._callbacks)
            for key,value in changed.items():
                for callback in callbacks: callback(key,previous[key],value)
            return normalized

    @staticmethod
    def _unknown(key): raise SettingsError(f"unknown setting: {key}")
    def reset(self,key=None):
        with self._lock:
            if key is None:
                self._data.clear()
            else:
                if key not in _spec_map():raise SettingsError(f"unknown setting: {key}")
                self._data.pop(key,None)
            self._save()

    def snapshot(self,include_defaults=True):
        if not include_defaults:return dict(self._data)
        return {spec.key:self.get(spec.key) for spec in SPECS}
    def schema(self): return SPECS
    def on_change(self,callback): self._callbacks.append(callback)
    def profile(self): return str(self.get("profile"))
    def set_profile(self,name):
        clean=str(name).strip()
        if not clean or any(ch in clean for ch in "/\\"): raise SettingsError("profile name must be a non-empty path-safe name")
        self.set("profile",clean)

def public_snapshot(settings=None):
    return (settings or AdvancedSettings()).snapshot()
