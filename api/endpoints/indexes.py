from fastapi import APIRouter
from api.utils.query import execute_query_cached
from api.sql.indexes import MISSING_INDEXES, UNUSED_INDEXES, DUPLICATE_INDEXES, BLOATED_INDEXES, UNINDEXED_FKS

router = APIRouter(prefix="/indexes", tags=["indexes"])

@router.get("/missing")
async def get_missing_indexes():
    return await execute_query_cached("300s", "/indexes/missing", {}, MISSING_INDEXES)

@router.get("/unused")
async def get_unused_indexes():
    return await execute_query_cached("300s", "/indexes/unused", {}, UNUSED_INDEXES)

@router.get("/duplicate")
async def get_duplicate_indexes():
    return await execute_query_cached("300s", "/indexes/duplicate", {}, DUPLICATE_INDEXES)

@router.get("/bloated")
async def get_bloated_indexes():
    return await execute_query_cached("300s", "/indexes/bloated", {}, BLOATED_INDEXES)

@router.get("/unindexed-fks")
async def get_unindexed_fks():
    return await execute_query_cached("300s", "/indexes/unindexed-fks", {}, UNINDEXED_FKS)
