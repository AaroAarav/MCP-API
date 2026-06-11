import os
import time
from typing import Optional
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection

# We use the sre_ops role for POST, and sre_read role for GET.
# But for simplicity in the connection pool, we might want two pools or just use sre_ops.
# The design document specifies: sre_read for GET, sre_ops for POST.
# Let's read from env vars. We'll set a default for local testing.

READ_DSN = os.getenv("SRE_READ_DB_URL", "postgresql://sre_read:sre_read_pass@postgres:5432/sre_db")
OPS_DSN = os.getenv("SRE_OPS_DB_URL", "postgresql://sre_ops:sre_ops_pass@postgres:5432/sre_db")

class DatabaseManager:
    def __init__(self):
        self.read_pool: Optional[AsyncConnectionPool] = None
        self.ops_pool: Optional[AsyncConnectionPool] = None
        self.pg_version: int = 0

    async def connect(self):
        self.read_pool = AsyncConnectionPool(READ_DSN, min_size=1, max_size=10)
        self.ops_pool = AsyncConnectionPool(OPS_DSN, min_size=1, max_size=5)
        
        # Wait for pools to initialize
        await self.read_pool.open()
        await self.ops_pool.open()

        # Fetch PG version
        async with self.read_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SHOW server_version_num;")
                res = await cur.fetchone()
                if res:
                    self.pg_version = int(res[0]) // 10000

    async def disconnect(self):
        if self.read_pool:
            await self.read_pool.close()
        if self.ops_pool:
            await self.ops_pool.close()

db_manager = DatabaseManager()

@asynccontextmanager
async def get_read_conn():
    if not db_manager.read_pool:
        raise RuntimeError("Read pool not initialized")
    async with db_manager.read_pool.connection() as conn:
        yield conn

@asynccontextmanager
async def get_ops_conn():
    if not db_manager.ops_pool:
        raise RuntimeError("Ops pool not initialized")
    async with db_manager.ops_pool.connection() as conn:
        yield conn
