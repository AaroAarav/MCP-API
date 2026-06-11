BLOCKING_LOCKS = """
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_query,
    blocking_activity.query AS blocking_query,
    blocked_locks.locktype,
    EXTRACT(EPOCH FROM (now() - blocked_activity.query_start)) AS wait_duration_seconds
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
"""

IDLE_IN_TRANSACTION = """
SELECT 
    pid, 
    usename, 
    state, 
    EXTRACT(EPOCH FROM (now() - state_change)) AS idle_duration_seconds,
    substring(query, 1, 100) AS query_text 
FROM pg_stat_activity 
WHERE state = 'idle in transaction' 
  AND EXTRACT(EPOCH FROM (now() - state_change)) > %(min_seconds)s;
"""

CONNECTIONS = """
SELECT 
    state, 
    count(*) as count 
FROM pg_stat_activity 
GROUP BY state;
"""

CANCEL_QUERY = """
SELECT pg_cancel_backend(%(pid)s);
"""

TERMINATE_SESSION = """
SELECT pg_terminate_backend(%(pid)s);
"""

VALIDATE_PID = """
SELECT backend_start FROM pg_stat_activity WHERE pid = %(pid)s;
"""
