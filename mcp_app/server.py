import os
import httpx
from mcp.server.fastmcp import FastMCP
import json
import logging
import inspect
import sys

# Configure extensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mcp_server.log"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("mcp_tools")

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080/api/v1")

mcp = FastMCP("postgres-sre-mcp")

def format_for_llm(resp: httpx.Response) -> str:
    try:
        data = resp.json()
    except Exception:
        return f"Error: Failed to parse API response. Status Code: {resp.status_code}"
    
    if not data.get("ok"):
        return f"Error: {data.get('error')}\nSuggestion: {data.get('suggestion', '')}"
    
    # Format into concise text/JSON
    return json.dumps(data.get("data", []), indent=2)

async def _api_get(endpoint: str, params: dict = None) -> str:
    caller = inspect.stack()[1].function
    logger.info(f"--- TOOL CALLED: {caller} ---")
    logger.info(f"Querying API: GET {endpoint} | Params: {params}")
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{API_BASE_URL}{endpoint}", params=params)
        result = format_for_llm(resp)
        logger.info(f"Result passed to LLM from {caller}:\n{result}\n-----------------------")
        return result

async def _api_post(endpoint: str, json_body: dict = None) -> str:
    caller = inspect.stack()[1].function
    logger.info(f"--- TOOL CALLED: {caller} ---")
    logger.info(f"Querying API: POST {endpoint} | Body: {json_body}")
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(f"{API_BASE_URL}{endpoint}", json=json_body or {})
        result = format_for_llm(resp)
        logger.info(f"Result passed to LLM from {caller}:\n{result}\n-----------------------")
        return result


@mcp.tool()
async def slow_queries(limit: int = 10, order_by: str = "total_time") -> str:
    """Returns the top N slowest queries right now."""
    return await _api_get("/queries/slow", {"limit": limit, "order_by": order_by})

@mcp.tool()
async def active_sessions() -> str:
    """Who is connected and what is each session doing?"""
    return await _api_get("/queries/active")

@mcp.tool()
async def long_running_queries(min_seconds: int = 30) -> str:
    """Which sessions have been running too long?"""
    return await _api_get("/queries/long-running", {"min_seconds": min_seconds})

@mcp.tool()
async def temp_spill_queries(limit: int = 10) -> str:
    """Which queries are spilling sorts or hashes to disk?"""
    return await _api_get("/queries/temp-spill", {"limit": limit})

@mcp.tool()
async def explain_query(query: str) -> str:
    """Show the execution plan for a given SQL statement."""
    return await _api_post("/queries/explain", {"query": query})

@mcp.tool()
async def blocking_lock_tree() -> str:
    """Who is blocking whom, what lock, and for how long?"""
    return await _api_get("/sessions/blocking")

@mcp.tool()
async def idle_in_transaction(min_seconds: int = 60) -> str:
    """Which sessions are stuck idle in transaction?"""
    return await _api_get("/sessions/idle-in-transaction", {"min_seconds": min_seconds})

@mcp.tool()
async def connection_utilization() -> str:
    """How close is the connection pool to max_connections?"""
    return await _api_get("/sessions/connections")

@mcp.tool()
async def cancel_query(pid: int, reason: str) -> str:
    """Cancel a query without dropping the connection."""
    return await _api_post(f"/sessions/{pid}/cancel", {"reason": reason})

@mcp.tool()
async def terminate_session(pid: int, reason: str, confirm: bool = True) -> str:
    """Disconnect a session entirely."""
    return await _api_post(f"/sessions/{pid}/terminate", {"reason": reason, "confirm": confirm})

@mcp.tool()
async def cache_hit_rates() -> str:
    """Is the buffer cache working? Which tables have low hit rates?"""
    return await _api_get("/cache/hit-rates")

@mcp.tool()
async def missing_indexes() -> str:
    """Which tables are doing too many sequential scans?"""
    return await _api_get("/indexes/missing")

@mcp.tool()
async def unused_indexes() -> str:
    """Which indexes add write overhead but are never read?"""
    return await _api_get("/indexes/unused")

@mcp.tool()
async def duplicate_indexes() -> str:
    """Which indexes are made redundant by another?"""
    return await _api_get("/indexes/duplicate")

@mcp.tool()
async def bloated_indexes() -> str:
    """Which indexes need a REINDEX?"""
    return await _api_get("/indexes/bloated")

@mcp.tool()
async def unindexed_fks() -> str:
    """Which foreign keys have no supporting index?"""
    return await _api_get("/indexes/unindexed-fks")

@mcp.tool()
async def table_bloat() -> str:
    """Which tables have too many dead tuples?"""
    return await _api_get("/tables/bloat")

@mcp.tool()
async def vacuum_status() -> str:
    """When did autovacuum last run on each table?"""
    return await _api_get("/tables/vacuum-status")

@mcp.tool()
async def statistics_staleness() -> str:
    """Which tables have stale planner statistics?"""
    return await _api_get("/tables/statistics-staleness")

@mcp.tool()
async def vacuum_progress() -> str:
    """How far along is the current VACUUM?"""
    return await _api_get("/tables/vacuum-progress")

@mcp.tool()
async def vacuum_table(name: str, confirm: bool = True) -> str:
    """Run VACUUM ANALYZE on a named table."""
    return await _api_post(f"/tables/{name}/vacuum", {"confirm": confirm})

@mcp.tool()
async def analyze_table(name: str, confirm: bool = True) -> str:
    """Refresh planner statistics for a named table."""
    return await _api_post(f"/tables/{name}/analyze", {"confirm": confirm})

@mcp.tool()
async def reindex_index(name: str, confirm: bool = True) -> str:
    """Rebuild a bloated index without locking the table."""
    return await _api_post(f"/indexes/{name}/reindex", {"confirm": confirm})

@mcp.tool()
async def replication_lag() -> str:
    """How far behind is the replica?"""
    return await _api_get("/replication/lag")

@mcp.tool()
async def schema_context() -> str:
    """Load a compact schema summary for the session."""
    return await _api_get("/schema/context")

if __name__ == "__main__":
    import sys
    if "--sse" in sys.argv:
        print("Starting SRE MCP Server on SSE transport...")
        mcp.run(transport="sse")
    else:
        mcp.run()
