TABLE_BLOAT = """
SELECT 
    relname AS table_name,
    n_dead_tup,
    n_live_tup,
    round((n_dead_tup::numeric / nullif(n_live_tup + n_dead_tup, 0)) * 100, 2) AS dead_tuple_ratio
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;
"""

VACUUM_STATUS = """
SELECT 
    relname AS table_name,
    last_autovacuum,
    last_autoanalyze,
    last_vacuum,
    last_analyze,
    n_dead_tup
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;
"""

STATISTICS_STALENESS = """
SELECT 
    relname AS table_name,
    n_mod_since_analyze,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_mod_since_analyze DESC
LIMIT 20;
"""

VACUUM_PROGRESS = """
SELECT 
    p.pid,
    p.datname,
    p.relid::regclass AS table_name,
    p.phase,
    p.heap_blks_total,
    p.heap_blks_scanned,
    p.heap_blks_vacuumed,
    p.index_vacuum_count,
    p.max_dead_tuple_bytes,
    p.num_dead_item_ids
FROM pg_stat_progress_vacuum p;
"""

REINDEX_PROGRESS = """
SELECT 
    p.pid,
    p.datname,
    p.relid::regclass AS table_name,
    p.index_relid::regclass AS index_name,
    p.phase,
    p.blocks_total,
    p.blocks_done,
    p.tuples_total,
    p.tuples_done
FROM pg_stat_progress_create_index p
WHERE p.command = 'REINDEX';
"""
