-- Production System Database Initialization Script
-- This script sets up the PostgreSQL database for the production system

-- Create database if it doesn't exist (handled by Docker)
-- CREATE DATABASE IF NOT EXISTS production_system;

-- Connect to the production_system database
\c production_system;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas for better organization
CREATE SCHEMA IF NOT EXISTS production;
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS config;

-- Set default search path
SET search_path TO public, production, auth, audit, config;

-- Create custom types
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('admin', 'operator', 'supervisor', 'viewer');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'production_status') THEN
        CREATE TYPE production_status AS ENUM ('running', 'stopped', 'error', 'maintenance');
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'quality_status') THEN
        CREATE TYPE quality_status AS ENUM ('good', 'warning', 'error');
    END IF;
END$$;

-- Create indexes for better performance
-- These will be created by SQLAlchemy, but we can add custom ones here

-- Performance monitoring views
CREATE OR REPLACE VIEW production_summary AS
SELECT 
    DATE(timestamp) as production_date,
    COUNT(*) as total_records,
    SUM(production_count) as total_production,
    AVG(cycle_time_ms) as avg_cycle_time,
    COUNT(CASE WHEN quality_status = 'good' THEN 1 END) as good_quality_count,
    COUNT(CASE WHEN quality_status = 'warning' THEN 1 END) as warning_quality_count,
    COUNT(CASE WHEN quality_status = 'error' THEN 1 END) as error_quality_count
FROM production_records 
GROUP BY DATE(timestamp)
ORDER BY production_date DESC;

-- User activity view
CREATE OR REPLACE VIEW user_activity AS
SELECT 
    u.username,
    u.role,
    u.last_login,
    COUNT(al.id) as total_actions,
    MAX(al.timestamp) as last_action
FROM users u
LEFT JOIN audit_logs al ON u.id = al.user_id
GROUP BY u.id, u.username, u.role, u.last_login
ORDER BY last_action DESC NULLS LAST;

-- System events summary
CREATE OR REPLACE VIEW system_events_summary AS
SELECT 
    event_type,
    severity,
    COUNT(*) as event_count,
    MAX(timestamp) as last_occurrence
FROM system_events
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY event_type, severity
ORDER BY event_count DESC;

-- Grant permissions
GRANT USAGE ON SCHEMA production TO postgres;
GRANT USAGE ON SCHEMA auth TO postgres;
GRANT USAGE ON SCHEMA audit TO postgres;
GRANT USAGE ON SCHEMA config TO postgres;

-- Create database user for the application (optional)
-- This is handled by the application configuration

-- Optimize PostgreSQL settings for production workload
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;

-- Note: These settings require a PostgreSQL restart to take effect
-- In a Docker environment, this happens automatically

COMMENT ON DATABASE production_system IS 'Production monitoring and control system database'; 