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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS long_term_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_key TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 0.8,
                    importance REAL NOT NULL DEFAULT 0.5,
                    access_count INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_memory_key
                ON long_term_memories(memory_key)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_category
                ON long_term_memories(category)
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

    def upsert_memory(self, memory_key, category, content, confidence=0.8, importance=0.5):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO long_term_memories
                    (memory_key, category, content, confidence, importance)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(memory_key) DO UPDATE SET
                    category=excluded.category,
                    content=excluded.content,
                    confidence=excluded.confidence,
                    importance=excluded.importance,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (memory_key, category, content, confidence, importance),
            )
            conn.commit()

    def search_memories(self, limit=8):
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, memory_key, category, content, confidence,
                       importance, access_count, created_at, updated_at
                FROM long_term_memories
                ORDER BY importance DESC, updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return rows

    def all_memories(self):
        with self._connect() as conn:
            return conn.execute(
                """
                SELECT id, memory_key, category, content, confidence,
                       importance, access_count, created_at, updated_at
                FROM long_term_memories
                ORDER BY updated_at DESC
                """
            ).fetchall()

    def touch_memories(self, ids):
        if not ids:
            return
        with self._connect() as conn:
            conn.executemany(
                """
                UPDATE long_term_memories
                SET access_count = access_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                [(int(memory_id),) for memory_id in ids],
            )
            conn.commit()

    def delete_memory(self, memory_key):
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM long_term_memories WHERE memory_key = ?",
                (memory_key,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def clear_memories(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM long_term_memories")
            conn.commit()

    def clear(self):
        with self._connect() as conn:
            conn.execute("DELETE FROM conversation_turns")
            conn.execute("DELETE FROM long_term_memories")
            conn.commit()
