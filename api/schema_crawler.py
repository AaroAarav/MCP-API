import asyncio
import json
from datetime import datetime, timezone
import psycopg
from fastapi import APIRouter
from api.services.db import READ_DSN, get_read_conn
from api.schemas.responses import APIResponse, APIErrorResponse

class SchemaContextManager:
    def __init__(self):
        self.context_cache = None
        self.last_generated = None
        self.table_details_cache = {}

    async def crawl_schema(self):
        """Build compact schema representation"""
        try:
            async with await psycopg.AsyncConnection.connect(READ_DSN) as conn:
                async with conn.cursor() as cur:
                    # Fetch all user tables and estimates
                    await cur.execute("""
                        SELECT n.nspname || '.' || c.relname AS qualified_name, c.relname, c.reltuples::bigint, n.nspname
                        FROM pg_class c 
                        JOIN pg_namespace n ON n.oid = c.relnamespace 
                        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast') AND c.relkind = 'r';
                    """)
                    tables_data = await cur.fetchall()
                    
                    tables = []
                    for qualified_name, tname, row_est, nspname in tables_data:
                        # Fetch columns
                        await cur.execute("""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE table_schema = %s AND table_name = %s 
                            ORDER BY ordinal_position;
                        """, (nspname, tname))
                        cols = await cur.fetchall()
                        col_str = ", ".join([f"{c[0]}:{c[1]}" for c in cols])
                        
                        # Fetch PK
                        await cur.execute("""
                            SELECT a.attname 
                            FROM pg_index i 
                            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) 
                            WHERE i.indrelid = %s::regclass AND i.indisprimary;
                        """, (tname,))
                        pk_res = await cur.fetchone()
                        pk = pk_res[0] if pk_res else None

                        # Fetch FKs
                        await cur.execute("""
                            SELECT conname, pg_get_constraintdef(oid) 
                            FROM pg_constraint 
                            WHERE conrelid = %s::regclass AND contype = 'f';
                        """, (tname,))
                        fks = [f[1] for f in await cur.fetchall()]

                        # Fetch Indexes
                        await cur.execute("""
                            SELECT indexrelname 
                            FROM pg_stat_user_indexes 
                            WHERE relname = %s;
                        """, (tname,))
                        indexes = [i[0] for i in await cur.fetchall()]

                        table_obj = {
                            "name": qualified_name,
                            "columns": col_str,
                            "pk": pk,
                            "fks": fks,
                            "row_estimate": row_est,
                            "indexes": indexes
                        }
                        tables.append(table_obj)
                        # pre-populate single table cache
                        self.table_details_cache[qualified_name] = table_obj
                    
                    self.context_cache = {
                        "tables": tables,
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "table_count": len(tables)
                    }
                    self.last_generated = datetime.now()
                    print("Schema context rebuilt.")
        except Exception as e:
            print(f"Error crawling schema: {e}")

    async def listen_for_ddl(self):
        """Listen for pg_notify events to invalidate cache"""
        # We need a dedicated connection for listening
        while True:
            try:
                async with await psycopg.AsyncConnection.connect(READ_DSN, autocommit=True) as conn:
                    await conn.execute("LISTEN ddl_events;")
                    generator = conn.notifies()
                    async for notify in generator:
                        print(f"Received DDL notification: {notify.payload}")
                        await self.crawl_schema()
            except Exception as e:
                print(f"Listen task error: {e}. Retrying in 5s.")
                await asyncio.sleep(5)

schema_manager = SchemaContextManager()
