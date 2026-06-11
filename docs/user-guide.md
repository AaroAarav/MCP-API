# PostgreSQL SRE MCP Server - User Guide

Welcome to the PostgreSQL SRE MCP Server. This tool empowers Site Reliability Engineers (SREs) and Database Administrators (DBAs) to interact with PostgreSQL databases through a Large Language Model (LLM) using natural language.

## Available Tools

The MCP server provides 25 specialized tools to diagnose and manage your PostgreSQL environment. These tools are exposed to the LLM, which can invoke them based on your natural language prompts.

1. **`slow_queries`**: Returns the top N slowest queries right now.
2. **`active_sessions`**: Shows who is connected and what each session is executing.
3. **`long_running_queries`**: Identifies sessions that have been running for an extended period.
4. **`temp_spill_queries`**: Finds queries spilling sorts or hashes to disk.
5. **`explain_query`**: Generates the execution plan for a specific SQL statement.
6. **`blocking_lock_tree`**: Analyzes the lock tree to show who is blocking whom, and for how long.
7. **`idle_in_transaction`**: Detects sessions stuck in an "idle in transaction" state.
8. **`connection_utilization`**: Shows how close the connection pool is to `max_connections`.
9. **`cancel_query`**: Cancels a running query without terminating the connection (requires `sre_ops` role).
10. **`terminate_session`**: Forcibly disconnects a session entirely (requires `sre_ops` role).
11. **`cache_hit_rates`**: Analyzes buffer cache performance and identifies tables with low hit rates.
12. **`missing_indexes`**: Finds tables performing excessive sequential scans due to missing indexes.
13. **`unused_indexes`**: Identifies indexes that add write overhead but are never utilized.
14. **`duplicate_indexes`**: Discovers redundant indexes.
15. **`bloated_indexes`**: Highlights indexes that require a `REINDEX`.
16. **`unindexed_fks`**: Finds foreign keys lacking supporting indexes.
17. **`table_bloat`**: Identifies tables with a high percentage of dead tuples.
18. **`vacuum_status`**: Shows when `autovacuum` last ran on each table.
19. **`statistics_staleness`**: Detects tables with outdated planner statistics.
20. **`vacuum_progress`**: Tracks the progress of ongoing `VACUUM` operations.
21. **`vacuum_table`**: Executes `VACUUM ANALYZE` on a specific table.
22. **`analyze_table`**: Refreshes planner statistics for a specific table.
23. **`reindex_index`**: Rebuilds a bloated index.
24. **`replication_lag`**: Measures how far behind a replica is from the primary.
25. **`schema_context`**: Loads a compact schema summary for the session.

## Effective Prompts

Here are 5 highly effective natural language prompts you can copy/paste to diagnose database issues quickly:

1. > "The application team is reporting sudden database timeouts. Check `active_sessions` and the `blocking_lock_tree` to see if there is a head blocker, then let me know if we need to `cancel_query`."
2. > "Analyze the `cache_hit_rates` and run `missing_indexes`. Are there any specific tables causing high I/O due to sequential scans?"
3. > "Look at `temp_spill_queries` and `slow_queries`. Which queries are running inefficient sorts, and can you `explain_query` for the worst offender?"
4. > "Check `table_bloat` and `bloated_indexes`. Identify any tables that urgently need a `vacuum_table` or indexes that should be rebuilt via `reindex_index`."
5. > "Are there any sessions `idle_in_transaction` for more than 5 minutes? If so, list them and recommend whether we should `terminate_session`."

## System Boundaries and Limits

> [!WARNING]
> To ensure the stability of the target database and the reliability of the LLM responses, several strict boundaries are enforced.

- **Read-Only by Default**: The majority of tools operate under the `sre_read` role. Only specific, explicit tools (like `cancel_query` or `terminate_session`) execute operations requiring the `sre_ops` role.
- **No Application Data Access**: The tools are restricted from accessing sensitive application data. They can query system catalogs (`pg_stat_activity`, `pg_class`, etc.) but cannot `SELECT * FROM users`.
- **Hard Row Limits**: To prevent overwhelming the LLM context window or the API layer, there is a hard server-side limit on rows returned (e.g., maximum of 100 rows per query). If a query exceeds this limit, results will be truncated.
- **Execution Timeouts**: The MCP server enforces HTTP timeouts (e.g., 10 seconds for GET requests, 30 seconds for POST requests) to prevent hanging API calls.
