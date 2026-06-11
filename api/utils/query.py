import time
from datetime import datetime, timezone
from api.services.db import get_read_conn
from api.cache.manager import cache_manager
from api.schemas.responses import APIResponse, APIErrorResponse

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

    try:
        async with get_read_conn() as conn:
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
    except Exception as e:
        return APIErrorResponse(ok=False, error=str(e))
