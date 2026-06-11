-- Enable pg_stat_statements extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Phase 5: Database Roles

-- 1. sre_read role
CREATE ROLE sre_read WITH LOGIN PASSWORD 'sre_read_pass';
GRANT pg_monitor TO sre_read;
-- Access to system catalogs is implicitly granted by pg_monitor for views like pg_stat_statements.
-- Explicitly deny access to application data
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM sre_read;
-- Wait, pg_monitor doesn't automatically grant SELECT on public schema, but we ensure no grants.

-- 2. sre_ops role
CREATE ROLE sre_ops WITH LOGIN PASSWORD 'sre_ops_pass';
GRANT pg_signal_backend TO sre_ops;
-- Grant VACUUM and ANALYZE privileges. PostgreSQL allows the table owner or superuser to vacuum.
-- Alternatively, we can grant the role to the table owners or use a specific function with SECURITY DEFINER.
-- Since PostgreSQL 16 allows granting MAINTAIN privilege on tables:
GRANT MAINTAIN ON ALL TABLES IN SCHEMA public TO sre_ops;

-- Ensure no data access
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM sre_ops;
