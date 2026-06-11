# MCP Specification

MCP Server is a thin wrapper over the API endpoints. It defines tools for the LLM.

## Tools List
- `slow_queries` -> `GET /queries/slow`
- `active_sessions` -> `GET /queries/active`
- `long_running_queries` -> `GET /queries/long-running`
- `temp_spill_queries` -> `GET /queries/temp-spill`
- `explain_query` -> `POST /queries/explain`
- `blocking_lock_tree` -> `GET /sessions/blocking`
- `idle_in_transaction` -> `GET /sessions/idle-in-transaction`
- `connection_utilization` -> `GET /sessions/connections`
- `cancel_query` -> `POST /sessions/{pid}/cancel`
- `terminate_session` -> `POST /sessions/{pid}/terminate`
- `cache_hit_rates` -> `GET /cache/hit-rates`
- `missing_indexes` -> `GET /indexes/missing`
- `unused_indexes` -> `GET /indexes/unused`
- `duplicate_indexes` -> `GET /indexes/duplicate`
- `bloated_indexes` -> `GET /indexes/bloated`
- `unindexed_fks` -> `GET /indexes/unindexed-fks`
- `table_bloat` -> `GET /tables/bloat`
- `vacuum_status` -> `GET /tables/vacuum-status`
- `statistics_staleness` -> `GET /tables/statistics-staleness`
- `vacuum_progress` -> `GET /tables/vacuum-progress`
- `vacuum_table` -> `POST /tables/{name}/vacuum`
- `analyze_table` -> `POST /tables/{name}/analyze`
- `reindex_index` -> `POST /indexes/{name}/reindex`
- `replication_lag` -> `GET /replication/lag`
- `schema_context` -> `GET /schema/context`

All tools must format API JSON response to an LLM-friendly plain text or condensed JSON format.
