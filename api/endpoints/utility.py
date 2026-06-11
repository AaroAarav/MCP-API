from fastapi import APIRouter
import sqlite3
import os
from api.schemas.responses import APIResponse, APIErrorResponse

router = APIRouter(prefix="", tags=["utility"])
DB_PATH = os.getenv("AUDIT_DB_PATH", "audit.sqlite")

@router.get("/audit-log")
async def get_audit_log(limit: int = 50):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT id, timestamp, actor, endpoint, target, success, duration_ms, result "
                "FROM audit_logs ORDER BY id DESC LIMIT ?", 
                (limit,)
            )
            rows = cur.fetchall()
            data = [dict(row) for row in rows]
            return APIResponse(ok=True, data=data, row_count=len(data), cached=False)
    except Exception as e:
        return APIErrorResponse(ok=False, error=str(e))
