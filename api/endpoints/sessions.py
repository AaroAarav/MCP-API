from fastapi import APIRouter, Query, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import time
from datetime import datetime

from api.services.db import get_read_conn
from api.cache.manager import cache_manager
from api.schemas.responses import APIResponse, APIErrorResponse
from api.sql.sessions import BLOCKING_LOCKS, IDLE_IN_TRANSACTION, CONNECTIONS

# Try to import our execute_query_cached helper. To avoid circular imports, we could duplicate or move it.
# We will just duplicate the basic logic for now.
async def execute_query_cached(ttl_category: str, endpoint: str, params: dict, sql: str, sql_params: dict = None):
    start_time = time.time()
    cached_result = cache_manager.get(ttl_category, endpoint, params)
    if cached_result is not None:
        return APIResponse(
            ok=True, data=cached_result["data"], row_count=len(cached_result["data"]),
            cached=True, cached_at=cached_result["cached_at"], execution_ms=int((time.time() - start_time) * 1000)
        )

    try:
        async with get_read_conn() as conn:
            async with conn.cursor() as cur:
                await cur.execute(sql, sql_params)
                columns = [desc[0] for desc in cur.description]
                rows = await cur.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
                cache_manager.set(ttl_category, endpoint, params, {"data": data, "cached_at": datetime.now()})
                return APIResponse(ok=True, data=data, row_count=len(data), cached=False, execution_ms=int((time.time() - start_time) * 1000))
    except Exception as e:
        return APIErrorResponse(ok=False, error=str(e))

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("/blocking")
async def get_blocking():
    return await execute_query_cached("10s", "/sessions/blocking", {}, BLOCKING_LOCKS)

@router.get("/idle-in-transaction")
async def get_idle(min_seconds: int = Query(60)):
    return await execute_query_cached("10s", "/sessions/idle-in-transaction", {"min_seconds": min_seconds}, IDLE_IN_TRANSACTION, {"min_seconds": min_seconds})

@router.get("/connections")
async def get_connections():
    # max_connections is usually accessible, but might require different pg view
    # For now we just return the counts
    return await execute_query_cached("10s", "/sessions/connections", {}, CONNECTIONS)
