import sqlite3
from pathlib import Path

from roster.models import ConversationTurn


class SQLiteMemoryStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _initialize(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add(self, role, content):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO conversation_turns (role, content) VALUES (?, ?)",
                (role, content),
            )
            conn.commit()

    def recent(self, limit=20):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content
                FROM conversation_turns
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        rows.reverse()
        return [ConversationTurn(role=role, content=content) for role, content in rows]

    def clear(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM conversation_turns")
            conn.commit()
