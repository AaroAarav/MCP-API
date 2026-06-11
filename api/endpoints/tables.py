from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time

from api.services.db import get_ops_conn, get_read_conn
from api.utils.query import execute_query_cached
from api.schemas.responses import APIResponse, APIErrorResponse
from api.audit.logger import audit_logger
from api.sql.tables import TABLE_BLOAT, VACUUM_STATUS, STATISTICS_STALENESS, VACUUM_PROGRESS, REINDEX_PROGRESS

router = APIRouter(prefix="", tags=["tables"])

@router.get("/tables/bloat")
async def get_bloat():
    return await execute_query_cached("120s", "/tables/bloat", {}, TABLE_BLOAT)

@router.get("/tables/vacuum-status")
async def get_vacuum_status():
    return await execute_query_cached("120s", "/tables/vacuum-status", {}, VACUUM_STATUS)

@router.get("/tables/statistics-staleness")
async def get_statistics_staleness():
    return await execute_query_cached("120s", "/tables/statistics-staleness", {}, STATISTICS_STALENESS)

@router.get("/tables/vacuum-progress")
async def get_vacuum_progress():
    return await execute_query_cached("120s", "/tables/vacuum-progress", {}, VACUUM_PROGRESS)

@router.get("/tables/reindex-progress")
async def get_reindex_progress():
    return await execute_query_cached("120s", "/tables/reindex-progress", {}, REINDEX_PROGRESS)

class ConfirmRequest(BaseModel):
    confirm: bool

@router.post("/tables/{name}/vacuum")
async def run_vacuum(name: str, req: ConfirmRequest):
    if not req.confirm:
        return APIErrorResponse(ok=False, error="confirm field must be true")
    
    start_time = time.time()
    actor = "mcp_client"
    log_id = audit_logger.log_intent(actor, f"/tables/{name}/vacuum", name)
    try:
        async with get_ops_conn() as conn:
            # We must use autocommit for VACUUM
            await conn.set_autocommit(True)
            async with conn.cursor() as cur:
                # Sanitize table name to prevent SQL injection (must be alphanumeric/underscores)
                if not name.replace('_', '').isalnum():
                    raise ValueError("Invalid table name")
                await cur.execute(f"VACUUM ANALYZE {name};")
        
        duration = int((time.time() - start_time) * 1000)
        audit_logger.log_result(log_id, True, duration, "Success")
        return APIResponse(ok=True, data=[{"vacuumed": name}], row_count=1, execution_ms=duration)
    except Exception as e:
        duration = int((time.time() - start_time) * 1000)
        audit_logger.log_result(log_id, False, duration, str(e))
        return APIErrorResponse(ok=False, error=str(e))

@router.post("/tables/{name}/analyze")
async def run_analyze(name: str, req: ConfirmRequest):
    if not req.confirm:
        return APIErrorResponse(ok=False, error="confirm field must be true")
    
    start_time = time.time()
    actor = "mcp_client"
    log_id = audit_logger.log_intent(actor, f"/tables/{name}/analyze", name)
    try:
        async with get_ops_conn() as conn:
            await conn.set_autocommit(True)
            async with conn.cursor() as cur:
                if not name.replace('_', '').isalnum():
                    raise ValueError("Invalid table name")
                await cur.execute(f"ANALYZE {name};")
        
        duration = int((time.time() - start_time) * 1000)
        audit_logger.log_result(log_id, True, duration, "Success")
        return APIResponse(ok=True, data=[{"analyzed": name}], row_count=1, execution_ms=duration)
    except Exception as e:
        duration = int((time.time() - start_time) * 1000)
        audit_logger.log_result(log_id, False, duration, str(e))
        return APIErrorResponse(ok=False, error=str(e))

@router.post("/indexes/{name}/reindex")
async def run_reindex(name: str, req: ConfirmRequest):
    if not req.confirm:
        return APIErrorResponse(ok=False, error="confirm field must be true")
    
    start_time = time.time()
    actor = "mcp_client"
    log_id = audit_logger.log_intent(actor, f"/indexes/{name}/reindex", name)
    try:
        async with get_ops_conn() as conn:
            await conn.set_autocommit(True)
            async with conn.cursor() as cur:
                if not name.replace('_', '').isalnum():
                    raise ValueError("Invalid index name")
                await cur.execute(f"REINDEX INDEX CONCURRENTLY {name};")
        
        duration = int((time.time() - start_time) * 1000)
        audit_logger.log_result(log_id, True, duration, "Success")
        return APIResponse(ok=True, data=[{"reindexed": name}], row_count=1, execution_ms=duration)
    except Exception as e:
        duration = int((time.time() - start_time) * 1000)
        audit_logger.log_result(log_id, False, duration, str(e))
        return APIErrorResponse(ok=False, error=str(e))
