"""Database - SQLite storage logic for Tag data."""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, List
from contextlib import contextmanager
from threading import Lock


class TagDatabase:

    def __init__(self, db_path: str = "tag_data.db"):
        self.db_path = db_path
        self.lock = Lock()
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registered_tags (
                    id TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tag_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_id TEXT NOT NULL,
                    cnt INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    FOREIGN KEY (tag_id) REFERENCES registered_tags(id)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tag_logs_tag_id 
                ON tag_logs(tag_id)
            """)

            conn.commit()

    def register_tag(self, tag_id: str, description: str) -> bool:
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        "INSERT INTO registered_tags (id, description, created_at) VALUES (?, ?, ?)",
                        (tag_id, description, datetime.now().isoformat())
                    )
                    conn.commit()
                    return True
                except sqlite3.IntegrityError:
                    return False

    def is_tag_registered(self, tag_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM registered_tags WHERE id = ?", (tag_id,))
            return cursor.fetchone() is not None

    def log_tag_data(self, tag_id: str, cnt: int, timestamp: datetime):
        with self.lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tag_logs (tag_id, cnt, timestamp, received_at) VALUES (?, ?, ?, ?)",
                    (tag_id, cnt, timestamp.isoformat(), datetime.now().isoformat())
                )
                conn.commit()

    def get_tag_status(self, tag_id: str) -> Optional[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, description FROM registered_tags WHERE id = ?",
                (tag_id,)
            )
            tag = cursor.fetchone()
            if not tag:
                return None

            cursor.execute("""
                SELECT cnt, timestamp FROM tag_logs 
                WHERE tag_id = ? 
                ORDER BY id DESC LIMIT 1
            """, (tag_id,))
            last_log = cursor.fetchone()

            return {
                "id": tag["id"],
                "description": tag["description"],
                "last_cnt": last_log["cnt"] if last_log else None,
                "last_seen": last_log["timestamp"] if last_log else None
            }

    def get_all_tags(self) -> List[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, description FROM registered_tags")
            tags = cursor.fetchall()

            result = []
            for tag in tags:
                status = self.get_tag_status(tag["id"])
                if status:
                    result.append(status)
            return result


db = TagDatabase()
