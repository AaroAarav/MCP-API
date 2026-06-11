from fastapi import FastAPI
import asyncio
from api.services.db import db_manager
from api.endpoints import queries, sessions, cache, indexes, tables, replication, schema, utility
from api.schema_crawler import schema_manager

app = FastAPI(title="PostgreSQL SRE API")

@app.on_event("startup")
async def startup():
    try:
        await db_manager.connect()
        # Start DDL listener as background task
        asyncio.create_task(schema_manager.listen_for_ddl())
    except Exception as e:
        print(f"Failed to connect to DB on startup: {e}")

@app.on_event("shutdown")
async def shutdown():
    await db_manager.disconnect()

# Add a simple health endpoint before adding routers
@app.get("/health")
async def health():
    return {"status": "ok", "pg_version": getattr(db_manager, "pg_version", None)}

app.include_router(queries.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(cache.router, prefix="/api/v1")
app.include_router(indexes.router, prefix="/api/v1")
app.include_router(tables.router, prefix="/api/v1")
app.include_router(replication.router, prefix="/api/v1")
app.include_router(schema.router, prefix="/api/v1")
app.include_router(utility.router, prefix="/api/v1")
