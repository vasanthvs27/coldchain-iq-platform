-- ============================================================================
-- 012_verify_schema.sql
-- ColdChain IQ Platform: Comprehensive Schema & Data Integrity Verification
-- Run this script in the Supabase SQL Editor to verify complete deployment.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. Table Existence Check (Expected: 19 tables + 1 view)
-- ----------------------------------------------------------------------------
SELECT 
    table_name,
    CASE 
        WHEN table_type = 'VIEW' THEN 'VIEW (OK)'
        ELSE 'BASE TABLE (OK)'
    END AS status
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN (
    'packaging', 'products', 'lots', 'shipments', 'loggers',
    'temperature_readings', 'custody_events', 'route_stops',
    'threshold_policies', 'excursion_reports', 'roles', 'users',
    'shipment_logger_assignments', 'packaging_product_compatibilities',
    'packaging_product_compatibility', 'compliance_reports',
    'audit_events', 'data_generation_runs', 'validation_results',
    'ground_truth_records'
  )
ORDER BY table_name;

-- ----------------------------------------------------------------------------
-- 2. Primary Key Verification
-- ----------------------------------------------------------------------------
SELECT 
    tc.table_name, 
    kcu.column_name AS primary_key_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
  ON tc.constraint_name = kcu.constraint_name
WHERE tc.table_schema = 'public' 
  AND tc.constraint_type = 'PRIMARY KEY'
ORDER BY tc.table_name;

-- ----------------------------------------------------------------------------
-- 3. Foreign Key Relationship Verification
-- ----------------------------------------------------------------------------
SELECT
    tc.table_name AS child_table,
    kcu.column_name AS foreign_key_column,
    ccu.table_name AS referenced_parent_table,
    ccu.column_name AS referenced_parent_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;

-- ----------------------------------------------------------------------------
-- 4. Row Level Security (RLS) Status Check
-- ----------------------------------------------------------------------------
SELECT 
    tablename,
    rowsecurity AS rls_enabled
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- ----------------------------------------------------------------------------
-- 5. Active RLS Policy Count per Table
-- ----------------------------------------------------------------------------
SELECT 
    tablename, 
    COUNT(*) AS policy_count
FROM pg_policies 
WHERE schemaname = 'public'
GROUP BY tablename
ORDER BY tablename;

-- ----------------------------------------------------------------------------
-- 6. Index Verification
-- ----------------------------------------------------------------------------
SELECT 
    tablename, 
    indexname, 
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public'
  AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- ----------------------------------------------------------------------------
-- 7. Master Seed Record Counts
-- ----------------------------------------------------------------------------
SELECT 'products' AS entity, COUNT(*) AS total_rows FROM products
UNION ALL
SELECT 'packaging', COUNT(*) FROM packaging
UNION ALL
SELECT 'threshold_policies', COUNT(*) FROM threshold_policies
UNION ALL
SELECT 'roles', COUNT(*) FROM roles
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'packaging_product_compatibilities', COUNT(*) FROM packaging_product_compatibilities
UNION ALL
SELECT 'loggers', COUNT(*) FROM loggers;

-- ----------------------------------------------------------------------------
-- 8. Data Integrity Diagnostics
-- (Checks for Orphan records, mismatches, or invalid data)
-- ----------------------------------------------------------------------------

-- 8a. Orphan Lots (Lots referencing non-existent products)
SELECT lot_id, product_id 
FROM lots 
WHERE product_id NOT IN (SELECT product_id FROM products);

-- 8b. Product / Lot Inconsistency on Shipments
-- (Shipment product_id must match lot's product_id)
SELECT s.shipment_id, s.product_id AS shipment_product, l.product_id AS lot_product
FROM shipments s
JOIN lots l ON s.lot_id = l.lot_id
WHERE s.product_id <> l.product_id;

-- 8c. Unassigned Logger Readings
SELECT r.reading_id, r.logger_id, r.shipment_id, r.recorded_at
FROM temperature_readings r
WHERE NOT EXISTS (
    SELECT 1 FROM shipment_logger_assignments a
    WHERE a.logger_id = r.logger_id
      AND a.shipment_id = r.shipment_id
      AND a.assigned_at <= r.recorded_at
      AND (a.unassigned_at IS NULL OR a.unassigned_at >= r.recorded_at)
)
AND r.reading_status = 'VALID';

-- 8d. Temperature Invariants (Violations of min < max)
SELECT product_id, minimum_temperature, maximum_temperature 
FROM products 
WHERE minimum_temperature >= maximum_temperature;
