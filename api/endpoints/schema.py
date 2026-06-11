from fastapi import APIRouter, HTTPException
from api.schema_crawler import schema_manager
from api.schemas.responses import APIResponse, APIErrorResponse
import time

router = APIRouter(prefix="/schema", tags=["schema"])

@router.get("/context")
async def get_schema_context():
    start_time = time.time()
    if not schema_manager.context_cache:
        await schema_manager.crawl_schema()
    
    return APIResponse(
        ok=True,
        data=[schema_manager.context_cache],
        row_count=1,
        cached=True,
        execution_ms=int((time.time() - start_time) * 1000)
    )

@router.get("/table/{name}")
async def get_table_schema(name: str):
    start_time = time.time()
    if not schema_manager.context_cache:
        await schema_manager.crawl_schema()
    
    table_data = schema_manager.table_details_cache.get(name)
    if not table_data:
        return APIErrorResponse(ok=False, error=f"Table {name} not found")

    return APIResponse(
        ok=True,
        data=[table_data],
        row_count=1,
        cached=True,
        execution_ms=int((time.time() - start_time) * 1000)
    )
