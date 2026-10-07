import sqlite3
from datetime import datetime,timezone
class LongTermMemory:
    def __init__(self,path):
        self.db=sqlite3.connect(path); self.db.execute('CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY,text TEXT,kind TEXT,created_at TEXT)'); self.db.commit()
    def remember(self,text,kind='fact'):
        self.db.execute('INSERT INTO memories(text,kind,created_at) VALUES(?,?,?)',(text,kind,datetime.now(timezone.utc).isoformat())); self.db.commit()
    def search(self,query,limit=8):
        return self.db.execute('SELECT text,kind,created_at FROM memories WHERE text LIKE ? ORDER BY id DESC LIMIT ?',(f'%{query}%',limit)).fetchall()
