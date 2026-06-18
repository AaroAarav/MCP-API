from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time

from api.services.db import get_read_conn
from api.utils.query import execute_query_cached
from api.schemas.responses import APIResponse, APIErrorResponse
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
