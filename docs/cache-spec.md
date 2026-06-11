# Cache Specification

TTL caching is required for all GET endpoints, based on parameter hashes.
POST endpoints must never be cached.

## Required TTLs
- `/queries/*` = 30s (Frequent updates, e.g., pg_stat_statements)
- `/sessions/*`, `/sessions/blocking` = 10s (Session state changes fast)
- `/cache/hit-rates`, `/cache/table/*` = 60s (Buffer stats move at medium pace)
- `/tables/bloat`, `/tables/vacuum-status`, `/tables/statistics-staleness`, `/tables/vacuum-progress`, `/tables/reindex-progress` = 120s (Table-level stats are slow)
- `/indexes/*` = 300s (Index usage rarely changes)
- `/schema/context`, `/schema/table/*` = 3600s (Schema changes are rare. Cache rebuilt automatically on DDL `pg_notify`).

## Cache Key
Cache key must incorporate the endpoint path and a hash of all query parameters.
