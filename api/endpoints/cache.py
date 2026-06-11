from fastapi import APIRouter
from api.utils.query import execute_query_cached
from api.sql.cache import CACHE_HIT_RATES, TABLE_CACHE_HIT

router = APIRouter(prefix="/cache", tags=["cache"])

@router.get("/hit-rates")
async def get_hit_rates():
    return await execute_query_cached("60s", "/cache/hit-rates", {}, CACHE_HIT_RATES)

@router.get("/table/{name}")
async def get_table_hit_rates(name: str):
    return await execute_query_cached("60s", f"/cache/table/{name}", {}, TABLE_CACHE_HIT, {"table_name": name})
