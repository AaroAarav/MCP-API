# API Specification

Base URL: `http://localhost:8080/api/v1`
Standard Response Envelope:
```json
{
  "ok": true,
  "data": [],
  "row_count": 0,
  "cached": true,
  "cached_at": "timestamp",
  "pg_version": 16,
  "execution_ms": 42
}
```

## Endpoints
### Query Performance
- `GET /queries/slow` - Top N slowest queries (limit, order_by).
- `GET /queries/active` - Current sessions.
- `GET /queries/long-running` - Sessions active > threshold.
- `GET /queries/temp-spill` - Queries writing to temp files.
- `POST /queries/explain` - EXPLAIN output for SQL string.

### Sessions & Locks
- `GET /sessions/blocking` - Lock wait chain.
- `GET /sessions/idle-in-transaction` - Stuck idle sessions.
- `GET /sessions/connections` - Connection count vs max.
- `POST /sessions/{pid}/cancel` - Cancel query (body: `{reason}`).
- `POST /sessions/{pid}/terminate` - Disconnect session (body: `{reason, confirm: true}`).

### Cache & Memory
- `GET /cache/hit-rates` - Buffer cache hit ratio.
- `GET /cache/table/{name}` - Hit rates for single table.

### Index Health
- `GET /indexes/missing` - Tables with high seq scans.
- `GET /indexes/unused` - Indexes with 0 scans.
- `GET /indexes/duplicate` - Redundant indexes.
- `GET /indexes/bloated` - Indexes >30% dead space.
- `GET /indexes/unindexed-fks` - FKs without indexes.

### Table Health
- `GET /tables/bloat` - Dead tuple ratio.
- `GET /tables/vacuum-status` - Last autovacuum/analyze.
- `GET /tables/statistics-staleness` - Stale planner stats.
- `GET /tables/vacuum-progress` - In-flight VACUUM.
- `GET /tables/reindex-progress` - In-flight REINDEX.
- `POST /tables/{name}/vacuum` - Run VACUUM ANALYZE.
- `POST /tables/{name}/analyze` - Run ANALYZE.
- `POST /indexes/{name}/reindex` - Run REINDEX INDEX CONCURRENTLY.

### Replication
- `GET /replication/lag` - Replica lag in bytes and seconds.

### Schema Context
- `GET /schema/context` - Compact schema summary.
- `GET /schema/table/{name}` - Full table detail.

### Utility
- `GET /health` - API health and DB reachability.
- `GET /audit-log` - Recent POST actions.
