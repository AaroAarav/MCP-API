# Database Specification

## Roles
The API interacts with PostgreSQL using least-privilege roles. No application data access is permitted.

### `sre_read`
- **Permissions**: `GRANT pg_monitor`
- **Access**: Reads `pg_stat_statements`, `pg_stat_activity`, `pg_locks`, `pg_stat_user_tables`, `pg_stat_user_indexes`, `information_schema`.
- **Restriction**: Cannot read application table data.

### `sre_ops`
- **Permissions**: `GRANT pg_signal_backend`
- **Access**: Can call `pg_cancel_backend` and `pg_terminate_backend`. Granted `VACUUM` / `ANALYZE` on specific tables.
- **Restriction**: Cannot read application data.

## Extensions
- `pg_stat_statements` must be installed and configured in `shared_preload_libraries`.

## Sample Database
Needs to simulate a realistic workload with tables: `users`, `orders`, `products`, `order_items`, `payments`, `sessions`, `audit_logs`.
Must support generation of slow queries, lock contention, long-running queries, temp spill, bloat, and index health issues.
