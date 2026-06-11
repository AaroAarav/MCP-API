import asyncio
import random
import time

try:
    import psycopg
except ImportError:
    print("psycopg not installed. Run: pip install psycopg")
    exit(1)

DSN = "postgresql://postgres:postgres@localhost:5432/sre_db"

async def slow_queries():
    """Generate sequential scans and bad joins."""
    async with await psycopg.AsyncConnection.connect(DSN) as conn:
        async with conn.cursor() as cur:
            while True:
                # Seq scan on users (status has no index)
                await cur.execute("SELECT count(*) FROM users WHERE status = 'inactive'")
                # Bad join (orders.user_id is unindexed)
                await cur.execute('''
                    SELECT u.username, o.total_amount 
                    FROM users u 
                    JOIN orders o ON u.id = o.user_id 
                    WHERE o.status = 'pending' LIMIT 100
                ''')
                await asyncio.sleep(2)

async def lock_contention():
    """Generate blocking lock trees."""
    async with await psycopg.AsyncConnection.connect(DSN) as conn_a:
        async with await psycopg.AsyncConnection.connect(DSN) as conn_b:
            while True:
                target_id = random.randint(1, 100)
                # Session A locks the row
                await conn_a.execute("BEGIN;")
                await conn_a.execute(f"UPDATE products SET stock = stock - 1 WHERE id = {target_id}")
                
                # Session B tries to lock the same row (will block)
                try:
                    await asyncio.wait_for(
                        conn_b.execute(f"UPDATE products SET stock = stock + 1 WHERE id = {target_id}"),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    pass
                
                await conn_a.execute("ROLLBACK;")
                await conn_b.execute("ROLLBACK;")
                await asyncio.sleep(1)

async def long_running():
    """Generate queries running too long using pg_sleep."""
    async with await psycopg.AsyncConnection.connect(DSN) as conn:
        async with conn.cursor() as cur:
            while True:
                await cur.execute("SELECT pg_sleep(45)")
                await asyncio.sleep(5)

async def temp_spills():
    """Generate large sorts/hashes that spill to disk."""
    async with await psycopg.AsyncConnection.connect(DSN) as conn:
        async with conn.cursor() as cur:
            while True:
                # Force a small work_mem for this session to guarantee a spill
                await cur.execute("SET work_mem = '1MB'")
                await cur.execute("SELECT user_id, sum(total_amount) FROM orders GROUP BY user_id ORDER BY sum(total_amount) DESC LIMIT 10")
                await cur.execute("RESET work_mem")
                await asyncio.sleep(5)

async def idle_in_transaction():
    """Generate idle in transaction sessions."""
    async with await psycopg.AsyncConnection.connect(DSN) as conn:
        async with conn.cursor() as cur:
            await cur.execute("BEGIN;")
            await cur.execute("SELECT 1;")
            # Just hang forever
            await asyncio.sleep(86400)

async def main():
    print("Starting SRE Workload Generator...")
    await asyncio.gather(
        slow_queries(),
        lock_contention(),
        long_running(),
        temp_spills(),
        idle_in_transaction()
    )

if __name__ == "__main__":
    asyncio.run(main())
