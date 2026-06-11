MISSING_INDEXES = """
SELECT 
    relname AS table_name, 
    seq_scan, 
    seq_tup_read, 
    idx_scan, 
    seq_tup_read / nullif(seq_scan, 0) AS rows_per_scan 
FROM pg_stat_user_tables 
WHERE seq_scan > 0 AND seq_tup_read > 0
ORDER BY seq_tup_read DESC 
LIMIT 20;
"""

UNUSED_INDEXES = """
SELECT 
    s.relname AS table_name, 
    s.indexrelname AS index_name, 
    s.idx_scan, 
    pg_size_pretty(pg_relation_size(s.indexrelid)) AS index_size 
FROM pg_stat_user_indexes s 
JOIN pg_index i ON s.indexrelid = i.indexrelid 
WHERE s.idx_scan = 0 
  AND i.indisunique IS FALSE 
ORDER BY pg_relation_size(s.indexrelid) DESC;
"""

DUPLICATE_INDEXES = """
SELECT 
    indrelid::regclass AS table_name, 
    array_agg(indexrelid::regclass) AS duplicate_indexes 
FROM pg_index 
GROUP BY indrelid, indkey, indclass 
HAVING count(*) > 1;
"""

BLOATED_INDEXES = """
-- simplified bloat estimation query
SELECT 
    schemaname, relname AS table_name, indexrelname AS index_name, 
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
-- proper bloat estimation requires pgstattuple or complex maths
-- placeholder for demonstration
LIMIT 20;
"""

UNINDEXED_FKS = """
SELECT 
    conrelid::regclass AS table_name, 
    conname AS fk_name, 
    a.attname AS column_name 
FROM pg_constraint c 
JOIN pg_attribute a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey) 
WHERE c.contype = 'f' 
  AND NOT EXISTS (
      SELECT 1 FROM pg_index i 
      WHERE i.indrelid = c.conrelid AND a.attnum = ANY(i.indkey)
  );
"""
