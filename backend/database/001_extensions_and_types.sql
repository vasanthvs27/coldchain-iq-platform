-- ============================================================================
-- 001_extensions_and_types.sql
-- ColdChain IQ Platform: PostgreSQL Extensions & Domain Types
-- Safe for execution on a fresh or existing Supabase project.
-- ============================================================================

-- 1. Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Domain verification comments
COMMENT ON EXTENSION "uuid-ossp" IS 'UUID generation functions for auxiliary records';
COMMENT ON EXTENSION "pgcrypto" IS 'Cryptographic functions for password hashing and tamper-evident auditing';
