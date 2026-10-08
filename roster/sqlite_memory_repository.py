"""SQLite-backed structured memory repository with isolated records."""
import json
import sqlite3
from pathlib import Path
from roster.memory_record import MemoryRecord
from roster.memory_policy import MemoryPolicy

class SQLiteMemoryRepository:
    def __init__(self,path,policy=None):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.policy=policy or MemoryPolicy(); self._init()
    def _connect(self): return sqlite3.connect(self.path)
    def _init(self):
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS structured_memories (key TEXT PRIMARY KEY,value TEXT NOT NULL,kind TEXT NOT NULL,confidence REAL NOT NULL,importance REAL NOT NULL,source TEXT NOT NULL,created_at TEXT NOT NULL,metadata TEXT NOT NULL)"""); db.commit()
    def save(self,record):
        if not self.policy.accepts(record.confidence,record.kind): return False
        with self._connect() as db:
            db.execute("""INSERT INTO structured_memories VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,kind=excluded.kind,confidence=excluded.confidence,importance=excluded.importance,source=excluded.source,created_at=excluded.created_at,metadata=excluded.metadata""",(record.key,record.value,record.kind,record.confidence,record.importance,record.source,record.created_at,json.dumps(record.metadata,sort_keys=True))); db.commit()
        return True
    def get(self,key):
        with self._connect() as db: row=db.execute("SELECT key,value,kind,confidence,importance,source,created_at,metadata FROM structured_memories WHERE key=?",(key,)).fetchone()
        if not row:return None
        return MemoryRecord(*row[:7],metadata=json.loads(row[7]))
    def all(self):
        with self._connect() as db: rows=db.execute("SELECT key,value,kind,confidence,importance,source,created_at,metadata FROM structured_memories ORDER BY key").fetchall()
        return tuple(MemoryRecord(*r[:7],metadata=json.loads(r[7])) for r in rows)
