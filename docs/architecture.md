# Architecture Specification

## Overview
Three-tier architecture designed for separation of concerns and security.
1. **LLM**: Understands intent, picks MCP tools, formats responses. No SQL generation, no DB connection.
2. **MCP Server (FastMCP)**: Maps tool names to HTTP API calls. No SQL, no DB connection, no business logic.
3. **REST API (FastAPI)**: Hard-coded SQL, connection pool, caching, schema context, JSON output.
4. **PostgreSQL**: Target database accessed via restricted roles (`sre_read`, `sre_ops`).

## Architecture Constraints
- The MCP server MUST NEVER connect directly to PostgreSQL.
- All SQL MUST live inside the REST API layer as named endpoints.
- The MCP layer must only make HTTP GET/POST requests.
- No direct database interaction or raw SQL generation by the LLM.

## Tech Stack
- **API**: FastAPI, async psycopg3, Python.
- **MCP**: FastMCP, Python.
- **Database**: PostgreSQL (v13+ supported).
