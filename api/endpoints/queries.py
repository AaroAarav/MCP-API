from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import time
from datetime import datetime, timezone
from pydantic import BaseModel

from api.services.db import get_read_conn
from api.cache.manager import cache_manager
from api.schemas.responses import APIResponse, APIErrorResponse
from api.sql.queries import SLOW_QUERIES, ACTIVE_SESSIONS, LONG_RUNNING_QUERIES, TEMP_SPILL_QUERIES

router = APIRouter(prefix="/queries", tags=["queries"])

class ExplainRequest(BaseModel):
    query: str

async def execute_query_cached(ttl_category: str, endpoint: str, params: dict, sql: str, sql_params: dict = None):
    start_time = time.time()
    
    # Check cache
    cached_result = cache_manager.get(ttl_category, endpoint, params)
    if cached_result is not None:
        return APIResponse(
            ok=True,
            data=cached_result["data"],
            row_count=len(cached_result["data"]),
            cached=True,
            cached_at=cached_result["cached_at"],
            execution_ms=int((time.time() - start_time) * 1000)
        )

    # Execute query
    try:
        async with get_read_conn() as conn:
            # Check for pg_stat_statements where necessary
            if 'pg_stat_statements' in sql:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT extname FROM pg_extension WHERE extname = 'pg_stat_statements';")
                    if not await cur.fetchone():
                        raise HTTPException(status_code=400, detail="pg_stat_statements not installed")

            async with conn.cursor() as cur:
                await cur.execute(sql, sql_params)
                columns = [desc[0] for desc in cur.description]
                rows = await cur.fetchall()
                data = [dict(zip(columns, row)) for row in rows]
                
                # Cache the result
                cache_manager.set(ttl_category, endpoint, params, {
                    "data": data,
                    "cached_at": datetime.now(timezone.utc)
                })

                return APIResponse(
                    ok=True,
                    data=data,
                    row_count=len(data),
                    cached=False,
                    cached_at=None,
                    execution_ms=int((time.time() - start_time) * 1000)
                )
    except HTTPException:
        raise
    except Exception as e:
        return APIErrorResponse(ok=False, error=str(e))


@router.get("/slow")
async def get_slow_queries(
    limit: int = Query(10, le=100), 
    order_by: str = Query("total_time", regex="^(total_time|mean_time|calls)$")
):
    order_map = {
        "total_time": "total_exec_time",
        "mean_time": "mean_exec_time",
        "calls": "calls"
    }
    sql = SLOW_QUERIES.format(order_by=order_map[order_by])
    return await execute_query_cached("30s", "/queries/slow", {"limit": limit, "order_by": order_by}, sql, {"limit": limit})

@router.get("/active")
async def get_active_sessions():
    return await execute_query_cached("10s", "/queries/active", {}, ACTIVE_SESSIONS)

@router.get("/long-running")
async def get_long_running(min_seconds: int = Query(30)):
    return await execute_query_cached("10s", "/queries/long-running", {"min_seconds": min_seconds}, LONG_RUNNING_QUERIES, {"min_seconds": min_seconds})

@router.get("/temp-spill")
async def get_temp_spill(limit: int = Query(10, le=100)):
    return await execute_query_cached("30s", "/queries/temp-spill", {"limit": limit}, TEMP_SPILL_QUERIES, {"limit": limit})

@router.post("/explain")
async def explain_query(req: ExplainRequest):
    start_time = time.time()
    try:
        async with get_read_conn() as conn:
            async with conn.cursor() as cur:
                # Never run EXPLAIN ANALYZE
                safe_query = req.query.replace("EXPLAIN ANALYZE", "EXPLAIN")
                await cur.execute(f"EXPLAIN {safe_query}")
                rows = await cur.fetchall()
                data = [{"Plan": row[0]} for row in rows]
                
                return APIResponse(
                    ok=True,
                    data=data,
                    row_count=len(data),
                    cached=False,
                    execution_ms=int((time.time() - start_time) * 1000)
                )
    except Exception as e:
        return APIErrorResponse(ok=False, error=str(e))
