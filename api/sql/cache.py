CACHE_HIT_RATES = """
SELECT 
    sum(blks_hit) * 100 / nullif(sum(blks_hit) + sum(blks_read), 0) AS cache_hit_ratio 
FROM pg_stat_database 
WHERE datname = current_database();
"""

TABLE_CACHE_HIT = """
SELECT 
    relname AS table_name,
    heap_blks_hit * 100 / nullif(heap_blks_hit + heap_blks_read, 0) AS heap_hit_ratio,
    idx_blks_hit * 100 / nullif(idx_blks_hit + idx_blks_read, 0) AS idx_hit_ratio,
    toast_blks_hit * 100 / nullif(toast_blks_hit + toast_blks_read, 0) AS toast_hit_ratio
FROM pg_statio_user_tables
WHERE relname = %(table_name)s;
"""
