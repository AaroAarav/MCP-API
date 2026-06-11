# Requirements Specification

## Functional Requirements
- Query Performance Analysis: Identify slow, active, long-running, and temp-spilling queries. EXPLAIN queries.
- Session and Lock Management: View blocking lock trees, idle-in-transaction sessions, connection utilization. Cancel and terminate sessions.
- Cache and Memory: Display buffer cache hit rates globally and per table.
- Index Health: Identify missing, unused, duplicate, bloated indexes, and unindexed foreign keys.
- Table Health: View table bloat, vacuum status, statistics staleness, and vacuum/reindex progress.
- Actions: Execute VACUUM, ANALYZE, REINDEX CONCURRENTLY via the API. Cancel and terminate queries/sessions.
- Replication: View replication lag.
- Schema Context: Provide a compact, token-efficient schema context for LLM sessions. Rebuild on DDL changes.

## Non-Functional Requirements
- **LLM/MCP Separation**: The LLM must not generate SQL. The MCP server must not generate SQL. All SQL is hard-coded in the REST API.
- **Performance**: The API should add minimal latency (<1ms). Endpoints should respond quickly via caching and connection pooling. Schema context must be token-efficient (e.g., ~600 tokens).
- **Result Limits**: API lists should default to 20 rows, with a hard server-side max of 100 to prevent LLM context overflow.
- **Caching**: Implement TTL-based caching per endpoint and parameter hash for GET endpoints.
- **Audit Logging**: All POST actions must be audit-logged before and after execution.

## Audit Requirements
- Every POST endpoint must be audited.
- Log before execution: actor, endpoint, target, timestamp.
- Log after execution: success/failure, duration, result.
