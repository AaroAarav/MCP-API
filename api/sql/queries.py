SLOW_QUERIES = """
SELECT 
    query, 
    calls, 
    total_exec_time / 1000 AS total_time_seconds, 
    mean_exec_time AS mean_time_ms, 
    rows 
FROM pg_stat_statements 
ORDER BY {order_by} DESC 
LIMIT %(limit)s;
"""

ACTIVE_SESSIONS = """
SELECT 
    pid, 
    usename, 
    application_name, 
    state, 
    wait_event_type, 
    wait_event, 
    query_start, 
    state_change, 
    EXTRACT(EPOCH FROM (now() - query_start)) AS duration_seconds,
    substring(query, 1, 100) AS query_text 
FROM pg_stat_activity 
WHERE state != 'idle' 
  AND pid != pg_backend_pid();
"""

LONG_RUNNING_QUERIES = """
SELECT 
    pid, 
    usename, 
    state, 
    EXTRACT(EPOCH FROM (now() - query_start)) AS duration_seconds,
    substring(query, 1, 100) AS query_text 
FROM pg_stat_activity 
WHERE state != 'idle' 
  AND pid != pg_backend_pid()
  AND EXTRACT(EPOCH FROM (now() - query_start)) > %(min_seconds)s;
"""

TEMP_SPILL_QUERIES = """
SELECT 
    query, 
    calls, 
    temp_blks_read, 
    temp_blks_written,
    (temp_blks_read + temp_blks_written) * 8192 AS temp_bytes
FROM pg_stat_statements 
WHERE temp_blks_written > 0 
ORDER BY temp_blks_written DESC 
LIMIT %(limit)s;
"""
