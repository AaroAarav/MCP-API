# Developer Guide

Welcome to the PostgreSQL SRE MCP Server repository! This guide provides engineers with the essential rules and workflows for contributing to the project.

## The Cardinal Rule: Where SQL Belongs

> [!CAUTION]
> **ALL SQL MUST LIVE IN THE REST API LAYER. NEVER IN THE MCP WRAPPER.**

Our architecture relies on strict separation between the Large Language Model context and our backend systems.
- The `mcp_app/server.py` file must contain **ZERO** raw SQL.
- The MCP server makes HTTP `GET` or `POST` requests to the FastAPI backend.
- The FastAPI layer (`api/endpoints/`) is the only component authorized to interact with `psycopg3` and execute SQL.

Violating this rule breaks our security boundary and risks exposing database credentials or enabling SQL injection via the LLM.

## How to Add a New Tool

Adding a new tool to the server is a two-step process: you first build the backend endpoint, and then you wrap it in the MCP server.

### Step 1: Create the FastAPI Endpoint

Navigate to the appropriate router in `api/endpoints/` (e.g., `api/endpoints/tables.py`) and create your endpoint.

```python
# api/endpoints/tables.py
from fastapi import APIRouter, Depends
from api.services.db import db_manager
from api.schemas.responses import APIResponse

# The router is included in api/app/main.py
@router.get("/tables/size")
async def table_sizes(limit: int = 10):
    """Get the size of the top largest tables."""
    sql = """
        SELECT relname AS table_name,
               pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size
        FROM pg_class c
        LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE nspname NOT IN ('pg_catalog', 'information_schema')
          AND c.relkind = 'r'
        ORDER BY pg_total_relation_size(c.oid) DESC
        LIMIT %s;
    """
    
    # Execute query using the internal db_manager
    rows = await db_manager.fetch_all(sql, (limit,))
    
    # Wrap in standard APIResponse
    return APIResponse(ok=True, data=rows, row_count=len(rows))
```

### Step 2: Wrap it in FastMCP

Next, expose your new endpoint to the LLM by defining a new tool in `mcp_app/server.py`. Use the pre-built `_api_get` or `_api_post` helpers.

```python
# mcp_app/server.py
from mcp.server.fastmcp import FastMCP
from server import _api_get # Assumes internal import

@mcp.tool()
async def largest_tables(limit: int = 10) -> str:
    """Which tables are taking up the most space on disk?"""
    # Only make HTTP calls to the API here! No SQL!
    return await _api_get("/tables/size", {"limit": limit})
```

> [!TIP]
> The docstring in the `@mcp.tool()` function (`"""Which tables are taking up..."""`) is critical. This string is passed directly to the LLM to help it understand when and why to use the tool. Make it clear and action-oriented.

## Writing Tests

Always back your new tool with tests in `tests/`. We enforce >90% code coverage. Mock the database interactions for unit testing the API, and mock the HTTP responses for unit testing the MCP wrapper.
