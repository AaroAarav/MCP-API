# PostgreSQL SRE MCP Server - Runbook

## API Down
**Symptoms**: LLM says "Error: Failed to parse API response". Health check fails.
**Action**:
1. Check API docker container: `docker logs postgres-sre-mcp-api-1`
2. Restart API: `docker-compose restart api`

## Database Connection Failing
**Symptoms**: API returns 500 or DB connection errors.
**Action**:
1. Verify PostgreSQL is up: `docker ps`
2. Check DB logs: `docker logs postgres-sre`
3. Check `SRE_READ_DB_URL` and `SRE_OPS_DB_URL` env vars.

## pg_stat_statements missing
**Symptoms**: API endpoints return `pg_stat_statements not installed`.
**Action**:
1. Verify `shared_preload_libraries=pg_stat_statements` is set in `postgresql.conf` or docker command.
2. Ensure `CREATE EXTENSION pg_stat_statements;` ran in the `postgres` db.
