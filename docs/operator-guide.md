# Operator Guide

## Overview
The SRE MCP Server connects a FastAPI middle-tier to your PostgreSQL cluster using restricted `sre_read` and `sre_ops` roles.

## Configuration
- `SRE_READ_DB_URL`: Connection string for the read-only role.
- `SRE_OPS_DB_URL`: Connection string for the ops role (used for VACUUM, CANCEL).
- `AUDIT_DB_PATH`: Path to the SQLite audit database.
- `API_BASE_URL`: URL the MCP Server uses to reach the API.

## DDL Tracking
To enable token-efficient schema context, ensure the DDL trigger is installed (see `04_triggers.sql`).
