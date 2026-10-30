-- ============================================================================
-- 003_create_supporting_tables.sql
-- ColdChain IQ Platform: Supporting Tables Schema
-- Covers RBAC, Assignments, Compatibility, Compliance, Auditing, Runs & Evaluation
-- ============================================================================

-- 1. Roles Table
CREATE TABLE IF NOT EXISTS roles (
    role_id VARCHAR(64) PRIMARY KEY,
    role_name VARCHAR(64) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(64) NOT NULL DEFAULT 'Logistics Analyst',
    organization VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Shipment Logger Assignments (Historical bridge linking loggers to shipments)
CREATE TABLE IF NOT EXISTS shipment_logger_assignments (
    assignment_id VARCHAR(64) PRIMARY KEY,
    shipment_id VARCHAR(64) NOT NULL REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    logger_id VARCHAR(64) NOT NULL REFERENCES loggers(logger_id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    unassigned_at TIMESTAMPTZ,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    assignment_notes TEXT
);

-- 4. Packaging Product Compatibility Bridge Table
CREATE TABLE IF NOT EXISTS packaging_product_compatibilities (
    id VARCHAR(64) PRIMARY KEY,
    product_id VARCHAR(64) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    packaging_id VARCHAR(64) NOT NULL REFERENCES packaging(packaging_id) ON DELETE CASCADE,
    qualified_status VARCHAR(32) NOT NULL DEFAULT 'QUALIFIED',
    max_transit_hours INTEGER NOT NULL DEFAULT 72,
    validation_notes TEXT,
    UNIQUE(product_id, packaging_id)
);

-- 4b. Compatibility View (enables both singular and plural table name queries)
CREATE OR REPLACE VIEW packaging_product_compatibility AS
SELECT * FROM packaging_product_compatibilities;

-- 5. Compliance Reports
CREATE TABLE IF NOT EXISTS compliance_reports (
    report_id VARCHAR(64) PRIMARY KEY,
    shipment_id VARCHAR(64) NOT NULL REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    product_id VARCHAR(64) REFERENCES products(product_id) ON DELETE SET NULL,
    lot_id VARCHAR(64) REFERENCES lots(lot_id) ON DELETE SET NULL,
    compliance_status VARCHAR(32) NOT NULL,
    compliance_score NUMERIC(5, 2) NOT NULL DEFAULT 100.00,
    total_readings INTEGER NOT NULL DEFAULT 0,
    valid_readings INTEGER NOT NULL DEFAULT 0,
    missing_readings INTEGER NOT NULL DEFAULT 0,
    excursion_count INTEGER NOT NULL DEFAULT 0,
    maximum_deviation NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    maximum_excursion_duration INTEGER NOT NULL DEFAULT 0,
    calibration_status VARCHAR(32) NOT NULL DEFAULT 'VALID',
    custody_completeness NUMERIC(5, 2) NOT NULL DEFAULT 100.00,
    policy_version VARCHAR(32) NOT NULL,
    reason_codes JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence_references JSONB NOT NULL DEFAULT '[]'::jsonb,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Audit Events (21 CFR Part 11 append-only log)
CREATE TABLE IF NOT EXISTS audit_events (
    event_id VARCHAR(64) PRIMARY KEY,
    entity_type VARCHAR(64) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    action VARCHAR(64) NOT NULL,
    user_id VARCHAR(64),
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Data Generation Runs
CREATE TABLE IF NOT EXISTS data_generation_runs (
    run_id VARCHAR(64) PRIMARY KEY,
    mode VARCHAR(32) NOT NULL DEFAULT 'STARTER', -- STARTER, FULL
    seed BIGINT NOT NULL DEFAULT 20261022,
    shipment_count INTEGER NOT NULL,
    logger_count INTEGER NOT NULL,
    reading_interval_minutes INTEGER NOT NULL DEFAULT 10,
    status VARCHAR(32) NOT NULL DEFAULT 'IN_PROGRESS',
    records_generated JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- 8. Validation Results
CREATE TABLE IF NOT EXISTS validation_results (
    validation_id VARCHAR(64) PRIMARY KEY,
    rule_name VARCHAR(128) NOT NULL,
    total_evaluated INTEGER NOT NULL,
    passed_count INTEGER NOT NULL,
    failed_count INTEGER NOT NULL,
    expected_anomalies INTEGER NOT NULL DEFAULT 0,
    unexpected_failures INTEGER NOT NULL DEFAULT 0,
    affected_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    status VARCHAR(32) NOT NULL DEFAULT 'PASSED',
    validated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 9. Ground Truth Storage (Isolated benchmark records for offline evaluation)
CREATE TABLE IF NOT EXISTS ground_truth_records (
    ground_truth_id VARCHAR(64) PRIMARY KEY,
    anomaly_id VARCHAR(64),
    issue_type VARCHAR(64) NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    expected_label VARCHAR(64) NOT NULL,
    expected_decision VARCHAR(64) NOT NULL,
    evidence_reference TEXT,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
