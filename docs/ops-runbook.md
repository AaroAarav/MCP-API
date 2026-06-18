# Operational Runbook

This runbook outlines operational procedures, health monitoring, and troubleshooting steps for the PostgreSQL SRE MCP Server and its underlying API.

## Health Monitoring

The FastAPI layer provides a `/health` endpoint to monitor the availability of the service and its connection to the database.

**Endpoint**: `GET /health`

### Normal Response
```json
{
  "status": "ok",
  "pg_version": "15.3 (Debian 15.3-1.pgdg110+1)"
}
```

### Understanding a "Degraded" Status

If the `/health` endpoint returns a `degraded` status, it indicates that the API is up and functioning, but certain critical database extensions or permissions are missing, reducing tool capability.

**Example Degraded Cause**: Missing `pg_stat_statements`
The `pg_stat_statements` extension is required by tools like `slow_queries` and `long_running_queries`. If the database lacks this extension (or if it's not preloaded in `postgresql.conf`), the API gracefully falls back. Tools relying on it will return empty or error responses, and the health endpoint will flag the degraded state.

**Resolution**: Ensure `pg_stat_statements` is included in `shared_preload_libraries` in your `postgresql.conf` and that `CREATE EXTENSION pg_stat_statements;` has been executed on the target database.

## Troubleshooting

### API Outage

**Symptom**: The LLM reports errors like `"Failed to parse API response. Status Code: 502"` or `"Connection refused"`.
**Diagnosis**: The MCP server is unable to reach the FastAPI backend via the `API_BASE_URL`.

**Steps**:
1. Check the Docker containers: `docker-compose ps`
2. Look for the API container status. If it's exited or continuously restarting, check the logs:
   ```bash
   docker-compose logs --tail=100 api
   ```
3. Common causes:
   - Invalid `DATABASE_URL` preventing the connection pool from initializing.
   - Network issues between the MCP process and the Docker network.
4. Once resolved, restart the API layer and verify `GET /health` returns `status: ok`.

### Stale DDL Cache

**Symptom**: The `schema_context` tool is returning outdated table definitions, or the LLM is attempting to query columns that no longer exist or missing recently added tables.
**Diagnosis**: The schema cache optimization is out of sync. Normally, DDL changes trigger a `LISTEN/NOTIFY` payload that invalidates the cache automatically.

**Steps**:
1. Check if the DDL listener background task is running. If the API logs show `Failed to connect to DB on startup`, the listener may have crashed.
2. Force a cache invalidation by calling the refresh endpoint directly (if exposed), or restart the API container to rebuild the cache from scratch:
   ```bash
   docker-compose restart api
   ```
5. Verify that the application user applying DDL changes to the database actually triggers the event trigger.

> [!WARNING]
> Repeatedly restarting the API will invalidate all application caches. Do so carefully in a production environment.
