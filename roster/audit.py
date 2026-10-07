"""Structured audit records for security-sensitive actions."""
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
import json
@dataclass(frozen=True)
class AuditRecord:
    action:str
    outcome:str
    actor:str="runtime"
    request_id:str|None=None
    detail:str|None=None
    timestamp:str=""
    def to_json(self)->str:
        payload=asdict(self)
        if not payload["timestamp"]: payload["timestamp"]=datetime.now(timezone.utc).isoformat()
        return json.dumps(payload,sort_keys=True)
