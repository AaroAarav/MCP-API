import sqlite3
import os
import json
from datetime import datetime, timezone
from typing import Optional

DB_PATH = os.getenv("AUDIT_DB_PATH", "audit.sqlite")

def init_audit_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                actor TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                target TEXT NOT NULL,
                success BOOLEAN,
                duration_ms INTEGER,
                result TEXT
            )
        ''')
        conn.commit()

init_audit_db()

class AuditLogger:
    @staticmethod
    def log_intent(actor: str, endpoint: str, target: str) -> int:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                "INSERT INTO audit_logs (timestamp, actor, endpoint, target) VALUES (?, ?, ?, ?)",
                (datetime.now(timezone.utc).isoformat(), actor, endpoint, target)
            )
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def log_result(log_id: int, success: bool, duration_ms: int, result: Optional[str] = None):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "UPDATE audit_logs SET success = ?, duration_ms = ?, result = ? WHERE id = ?",
                (success, duration_ms, result, log_id)
            )
            conn.commit()

audit_logger = AuditLogger()
