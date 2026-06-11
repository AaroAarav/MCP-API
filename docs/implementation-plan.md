# Implementation Plan

## Phase 1: Project Structure
Create the repository structure as defined in the request.

## Phase 2 & 3: Sample Database & SRE Test Data
Create a realistic PostgreSQL sample environment with millions of rows, specific tables, and workload simulation scripts to intentionally generate bloat, lock contention, slow queries, and index issues.

## Phase 4: Docker Environment
Configure `docker-compose.yml` for PostgreSQL, FastAPI, and MCP Server. Include `pg_stat_statements`.

## Phase 5: Database Roles
Bootstrap `sre_read` and `sre_ops` roles.

## Phase 6: FastAPI Implementation
Implement the API endpoints, separating SQL files, using pydantic models, async psycopg3, and standard response envelopes.

## Phase 7: Cache Layer
Implement TTL caching with parameter hashing.

## Phase 8: Schema Context System
Implement the `/schema/context` endpoint and automatic DDL change detection via `LISTEN/NOTIFY`.

## Phase 9: Audit Logging
Implement the audit system for POST endpoints.

## Phase 10: MCP Implementation
Implement FastMCP server with 25 tools mapping to API endpoints.

## Phase 11: Testing
Write pytest suite for >90% coverage.

## Phase 12: Observability
Add structured logging, health checks, and metrics. Handle missing pg_stat_statements gracefully.

## Phase 13: Security Review
Verify no direct DB access, role separation, PID recycling protection, and audit logs. Document in `security-review.md`.

## Phase 14: Documentation
Create `README.md`, `operator-guide.md`, and `runbook.md`.

## Open Questions
- Where does the audit log live? (Local SQLite, flat file, or separate PostgreSQL schema?)
- Should `db_profile` be set at startup or per-request?
- How to handle multi-team RBAC for `cancel_query` / `terminate_session`?
