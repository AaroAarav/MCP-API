# Security Review

## Threat Model & Mitigations
1. **SQL Injection**: Prevented because no SQL is generated dynamically by the LLM or MCP Server. The REST API uses parameterized queries (`psycopg`) for any parameters.
2. **Direct Database Access**: Prevented. The MCP Server only communicates via HTTP to the FastAPI REST API. The database port is not exposed to the LLM.
3. **Data Exfiltration**: The `sre_read` and `sre_ops` roles are explicitly stripped of access to public schema tables. The API can only read system catalogs (`pg_stat_*`, `pg_locks`, `information_schema`).
4. **PID Recycling**: The `/sessions/{pid}/cancel` and `terminate` endpoints require the PID and cross-check the `backend_start` timestamp (if provided) or operate with the assumption that SRE knows the risk. The design mitigates this by restricting `sre_ops` privileges.
5. **Audit Logging**: Every destructive action (POST) is audited via `api/audit/logger.py` tracking actor, action, timestamp, and result.
6. **Denial of Service**: Caching handles duplicate reads efficiently. `VACUUM FULL` is intentionally excluded to avoid exclusive locks.
