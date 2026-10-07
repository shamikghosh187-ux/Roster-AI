import sqlite3
from pathlib import Path

from roster.tasks import Task


class SQLiteTaskStore:
    def __init__(self, path):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self):
        with self._connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )"""
            )

    def save(self, task):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tasks (id, title, status) VALUES (?, ?, ?)",
                (task.id, task.title, task.status),
            )

    def get(self, task_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, title, status FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        return None if row is None else Task(title=row["title"], status=row["status"], id=row["id"])

    def list(self, status=None):
        query = "SELECT id, title, status FROM tasks"
        params = ()
        if status is not None:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY created_at DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [Task(title=row["title"], status=row["status"], id=row["id"]) for row in rows]

    def delete(self, task_id):
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount == 1
