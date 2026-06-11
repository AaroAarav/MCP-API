from fastapi import APIRouter
from api.utils.query import execute_query_cached
from api.sql.replication import REPLICATION_LAG

router = APIRouter(prefix="/replication", tags=["replication"])

@router.get("/lag")
async def get_replication_lag():
    # If not a primary or no replication, this returns empty.
    # We could also use pg_stat_wal_receiver to check if this is a standby and what the lag is.
    # The query in REPLICATION_LAG is for a primary checking its standbys. 
    # To check lag on the standby itself:
    STANDBY_LAG = """
    SELECT 
        pg_last_wal_receive_lsn() as receive_lsn,
        pg_last_wal_replay_lsn() as replay_lsn,
        EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))::int AS lag_seconds
    WHERE pg_is_in_recovery();
    """
    
    # We will try both, but for simplicity let's use the standby lag query as the spec says "On a standby"
    return await execute_query_cached("10s", "/replication/lag", {}, STANDBY_LAG)
