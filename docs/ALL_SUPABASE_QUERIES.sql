-- ============================================================================
-- ALL_SUPABASE_QUERIES.sql
-- ColdChain IQ Platform: Consolidated Master Schema & Master Seed Data
-- ============================================================================
-- Execute this entire script directly in the Supabase SQL Editor.
-- Target Database: Managed Supabase PostgreSQL
-- ============================================================================

-- ============================================================================
-- PART 1: EXTENSIONS & DOMAIN FUNCTIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- PART 2: 10 CORE TABLES
-- ============================================================================

-- 1. Packaging Table
CREATE TABLE IF NOT EXISTS packaging (
    packaging_id VARCHAR(64) PRIMARY KEY,
    packaging_name VARCHAR(255) NOT NULL,
    packaging_type VARCHAR(64) NOT NULL,
    minimum_temperature NUMERIC(5, 2) NOT NULL,
    maximum_temperature NUMERIC(5, 2) NOT NULL,
    validated_duration INTEGER NOT NULL, -- duration in hours
    insulation_type VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'QUALIFIED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(64) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    product_category VARCHAR(128) NOT NULL,
    minimum_temperature NUMERIC(5, 2) NOT NULL,
    maximum_temperature NUMERIC(5, 2) NOT NULL,
    allowed_excursion_duration INTEGER NOT NULL DEFAULT 60, -- duration in minutes
    default_packaging_id VARCHAR(64) REFERENCES packaging(packaging_id) ON DELETE SET NULL,
    shelf_life_days INTEGER NOT NULL DEFAULT 365,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    effective_until TIMESTAMPTZ,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE'
);

-- 3. Lots Table
CREATE TABLE IF NOT EXISTS lots (
    lot_id VARCHAR(64) PRIMARY KEY,
    product_id VARCHAR(64) NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    supplier_name VARCHAR(255) NOT NULL,
    manufacturing_date TIMESTAMPTZ NOT NULL,
    expiry_date TIMESTAMPTZ NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit VARCHAR(32) NOT NULL DEFAULT 'DOSES',
    lifecycle_status VARCHAR(32) NOT NULL DEFAULT 'RELEASED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Shipments Table
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id VARCHAR(64) PRIMARY KEY,
    lot_id VARCHAR(64) NOT NULL REFERENCES lots(lot_id) ON DELETE RESTRICT,
    product_id VARCHAR(64) NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    packaging_id VARCHAR(64) NOT NULL REFERENCES packaging(packaging_id) ON DELETE RESTRICT,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    carrier_name VARCHAR(255) NOT NULL,
    planned_departure TIMESTAMPTZ NOT NULL,
    actual_departure TIMESTAMPTZ,
    expected_arrival TIMESTAMPTZ NOT NULL,
    actual_arrival TIMESTAMPTZ,
    shipment_status VARCHAR(32) NOT NULL DEFAULT 'SCHEDULED',
    compliance_status VARCHAR(32) NOT NULL DEFAULT 'UNDER_REVIEW',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Loggers Table
CREATE TABLE IF NOT EXISTS loggers (
    logger_id VARCHAR(64) PRIMARY KEY,
    serial_number VARCHAR(128) UNIQUE NOT NULL,
    model VARCHAR(128) NOT NULL,
    calibration_date TIMESTAMPTZ NOT NULL,
    calibration_expiry TIMESTAMPTZ NOT NULL,
    accuracy_tolerance NUMERIC(4, 2) NOT NULL DEFAULT 0.50,
    measurement_uncertainty NUMERIC(4, 2) NOT NULL DEFAULT 0.20,
    battery_status NUMERIC(5, 2) NOT NULL DEFAULT 100.00,
    logger_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Temperature Readings Table
CREATE TABLE IF NOT EXISTS temperature_readings (
    reading_id VARCHAR(128) PRIMARY KEY,
    logger_id VARCHAR(64) NOT NULL REFERENCES loggers(logger_id) ON DELETE CASCADE,
    shipment_id VARCHAR(64) NOT NULL REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    recorded_at TIMESTAMPTZ NOT NULL,
    measured_temperature NUMERIC(5, 2) NOT NULL,
    corrected_temperature NUMERIC(5, 2) NOT NULL,
    calibration_uncertainty NUMERIC(4, 2) NOT NULL DEFAULT 0.20,
    reading_status VARCHAR(32) NOT NULL DEFAULT 'VALID',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Custody Events Table
CREATE TABLE IF NOT EXISTS custody_events (
    custody_event_id VARCHAR(64) PRIMARY KEY,
    shipment_id VARCHAR(64) NOT NULL REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    previous_custodian VARCHAR(255) NOT NULL,
    new_custodian VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    handoff_timestamp TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    acknowledgement_status VARCHAR(32) NOT NULL DEFAULT 'CONFIRMED',
    verification_status VARCHAR(32) NOT NULL DEFAULT 'VERIFIED',
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. Route Stops Table
CREATE TABLE IF NOT EXISTS route_stops (
    route_stop_id VARCHAR(64) PRIMARY KEY,
    shipment_id VARCHAR(64) NOT NULL REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    stop_sequence INTEGER NOT NULL,
    stop_name VARCHAR(255) NOT NULL,
    stop_type VARCHAR(64) NOT NULL,
    planned_arrival TIMESTAMPTZ NOT NULL,
    actual_arrival TIMESTAMPTZ,
    departure_time TIMESTAMPTZ,
    dwell_duration INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(32) NOT NULL DEFAULT 'COMPLETED'
);

-- 9. Threshold Policies Table
CREATE TABLE IF NOT EXISTS threshold_policies (
    policy_id VARCHAR(64) PRIMARY KEY,
    product_id VARCHAR(64) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    minimum_temperature NUMERIC(5, 2) NOT NULL,
    maximum_temperature NUMERIC(5, 2) NOT NULL,
    allowed_excursion_duration INTEGER NOT NULL DEFAULT 60,
    effective_from TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    effective_until TIMESTAMPTZ,
    policy_version VARCHAR(32) NOT NULL DEFAULT 'v1.0',
    policy_status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 10. Excursion Reports Table
CREATE TABLE IF NOT EXISTS excursion_reports (
    excursion_id VARCHAR(64) PRIMARY KEY,
    shipment_id VARCHAR(64) NOT NULL REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    product_id VARCHAR(64) NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    lot_id VARCHAR(64) NOT NULL REFERENCES lots(lot_id) ON DELETE RESTRICT,
    logger_id VARCHAR(64) NOT NULL REFERENCES loggers(logger_id) ON DELETE RESTRICT,
    start_timestamp TIMESTAMPTZ NOT NULL,
    end_timestamp TIMESTAMPTZ NOT NULL,
    calculated_duration INTEGER NOT NULL,
    minimum_observed_temperature NUMERIC(5, 2) NOT NULL,
    maximum_observed_temperature NUMERIC(5, 2) NOT NULL,
    severity VARCHAR(32) NOT NULL DEFAULT 'MEDIUM',
    issue_type VARCHAR(64) NOT NULL,
    investigation_status VARCHAR(32) NOT NULL DEFAULT 'OPEN',
    compliance_decision VARCHAR(32) NOT NULL DEFAULT 'UNDER_REVIEW',
    evidence_reference TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- PART 3: SUPPORTING TABLES
-- ============================================================================

-- Roles Table
CREATE TABLE IF NOT EXISTS roles (
    role_id VARCHAR(64) PRIMARY KEY,
    role_name VARCHAR(64) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Users Table
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

-- Shipment Logger Assignments
CREATE TABLE IF NOT EXISTS shipment_logger_assignments (
    assignment_id VARCHAR(64) PRIMARY KEY,
    shipment_id VARCHAR(64) NOT NULL REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    logger_id VARCHAR(64) NOT NULL REFERENCES loggers(logger_id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    unassigned_at TIMESTAMPTZ,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    assignment_notes TEXT
);

-- Packaging Product Compatibility
CREATE TABLE IF NOT EXISTS packaging_product_compatibilities (
    id VARCHAR(64) PRIMARY KEY,
    product_id VARCHAR(64) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    packaging_id VARCHAR(64) NOT NULL REFERENCES packaging(packaging_id) ON DELETE CASCADE,
    qualified_status VARCHAR(32) NOT NULL DEFAULT 'QUALIFIED',
    max_transit_hours INTEGER NOT NULL DEFAULT 72,
    validation_notes TEXT,
    UNIQUE(product_id, packaging_id)
);

CREATE OR REPLACE VIEW packaging_product_compatibility AS
SELECT * FROM packaging_product_compatibilities;

-- Compliance Reports
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

-- Audit Events (21 CFR Part 11)
CREATE TABLE IF NOT EXISTS audit_events (
    event_id VARCHAR(64) PRIMARY KEY,
    entity_type VARCHAR(64) NOT NULL,
    entity_id VARCHAR(64) NOT NULL,
    action VARCHAR(64) NOT NULL,
    user_id VARCHAR(64),
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Data Generation Runs
CREATE TABLE IF NOT EXISTS data_generation_runs (
    run_id VARCHAR(64) PRIMARY KEY,
    mode VARCHAR(32) NOT NULL DEFAULT 'STARTER',
    seed BIGINT NOT NULL DEFAULT 20261022,
    shipment_count INTEGER NOT NULL,
    logger_count INTEGER NOT NULL,
    reading_interval_minutes INTEGER NOT NULL DEFAULT 10,
    status VARCHAR(32) NOT NULL DEFAULT 'IN_PROGRESS',
    records_generated JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Validation Results
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

-- Ground Truth Records
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

-- ============================================================================
-- PART 4: INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_shipments_product_id ON shipments(product_id);
CREATE INDEX IF NOT EXISTS idx_shipments_lot_id ON shipments(lot_id);
CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(shipment_status);
CREATE INDEX IF NOT EXISTS idx_shipments_compliance ON shipments(compliance_status);
CREATE INDEX IF NOT EXISTS idx_shipments_planned_departure ON shipments(planned_departure);

CREATE INDEX IF NOT EXISTS idx_temp_readings_shipment ON temperature_readings(shipment_id);
CREATE INDEX IF NOT EXISTS idx_temp_readings_logger ON temperature_readings(logger_id);
CREATE INDEX IF NOT EXISTS idx_temp_readings_recorded_at ON temperature_readings(recorded_at);
CREATE INDEX IF NOT EXISTS idx_temp_readings_shipment_time ON temperature_readings(shipment_id, recorded_at ASC);
CREATE INDEX IF NOT EXISTS idx_temp_readings_status ON temperature_readings(reading_status);

CREATE INDEX IF NOT EXISTS idx_custody_shipment ON custody_events(shipment_id);
CREATE INDEX IF NOT EXISTS idx_custody_timestamp ON custody_events(handoff_timestamp ASC);

CREATE INDEX IF NOT EXISTS idx_route_stops_shipment ON route_stops(shipment_id);
CREATE INDEX IF NOT EXISTS idx_route_stops_sequence ON route_stops(shipment_id, stop_sequence ASC);

CREATE INDEX IF NOT EXISTS idx_excursions_shipment ON excursion_reports(shipment_id);
CREATE INDEX IF NOT EXISTS idx_excursions_severity ON excursion_reports(severity);
CREATE INDEX IF NOT EXISTS idx_excursions_status ON excursion_reports(investigation_status);

CREATE INDEX IF NOT EXISTS idx_policies_product ON threshold_policies(product_id);
CREATE INDEX IF NOT EXISTS idx_policies_status ON threshold_policies(policy_status);

CREATE INDEX IF NOT EXISTS idx_assignments_shipment_logger ON shipment_logger_assignments(shipment_id, logger_id);
CREATE INDEX IF NOT EXISTS idx_assignments_dates ON shipment_logger_assignments(assigned_at, unassigned_at);

CREATE INDEX IF NOT EXISTS idx_compliance_reports_shipment ON compliance_reports(shipment_id);
CREATE INDEX IF NOT EXISTS idx_compliance_reports_status ON compliance_reports(compliance_status);

CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_events(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_events(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ground_truth_entity ON ground_truth_records(entity_id);
CREATE INDEX IF NOT EXISTS idx_ground_truth_type ON ground_truth_records(issue_type);

-- ============================================================================
-- PART 5: CHECK CONSTRAINTS
-- ============================================================================
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_product_temp_range') THEN
        ALTER TABLE products ADD CONSTRAINT chk_product_temp_range CHECK (minimum_temperature < maximum_temperature);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_policy_temp_range') THEN
        ALTER TABLE threshold_policies ADD CONSTRAINT chk_policy_temp_range CHECK (minimum_temperature < maximum_temperature);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_packaging_temp_range') THEN
        ALTER TABLE packaging ADD CONSTRAINT chk_packaging_temp_range CHECK (minimum_temperature < maximum_temperature);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_stop_dwell_nonneg') THEN
        ALTER TABLE route_stops ADD CONSTRAINT chk_stop_dwell_nonneg CHECK (dwell_duration >= 0);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_excursion_duration_nonneg') THEN
        ALTER TABLE excursion_reports ADD CONSTRAINT chk_excursion_duration_nonneg CHECK (calculated_duration >= 0);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_excursion_time_order') THEN
        ALTER TABLE excursion_reports ADD CONSTRAINT chk_excursion_time_order CHECK (start_timestamp <= end_timestamp);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_compliance_score_range') THEN
        ALTER TABLE compliance_reports ADD CONSTRAINT chk_compliance_score_range CHECK (compliance_score >= 0.00 AND compliance_score <= 100.00);
    END IF;
END $$;

-- ============================================================================
-- PART 6: STORED FUNCTIONS & TRIGGERS
-- ============================================================================
CREATE OR REPLACE FUNCTION set_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_products_updated_at ON products;
CREATE TRIGGER trg_products_updated_at
BEFORE UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION set_updated_at_column();

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION set_updated_at_column();

CREATE OR REPLACE FUNCTION is_logger_assigned_to_shipment(
    p_logger_id VARCHAR(64),
    p_shipment_id VARCHAR(64),
    p_timestamp TIMESTAMPTZ
)
RETURNS BOOLEAN AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM shipment_logger_assignments
    WHERE logger_id = p_logger_id
      AND shipment_id = p_shipment_id
      AND assigned_at <= p_timestamp
      AND (unassigned_at IS NULL OR unassigned_at >= p_timestamp);
    RETURN (v_count > 0);
END;
$$ LANGUAGE plpgsql STABLE;

CREATE OR REPLACE FUNCTION calculate_shipment_excursion_duration(
    p_shipment_id VARCHAR(64)
)
RETURNS INTEGER AS $$
DECLARE
    v_total_minutes INTEGER;
BEGIN
    SELECT COALESCE(SUM(calculated_duration), 0) INTO v_total_minutes
    FROM excursion_reports
    WHERE shipment_id = p_shipment_id;
    RETURN v_total_minutes;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- PART 7: ENABLE ROW LEVEL SECURITY & POLICIES
-- ============================================================================
ALTER TABLE packaging ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE lots ENABLE ROW LEVEL SECURITY;
ALTER TABLE shipments ENABLE ROW LEVEL SECURITY;
ALTER TABLE loggers ENABLE ROW LEVEL SECURITY;
ALTER TABLE temperature_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE custody_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE route_stops ENABLE ROW LEVEL SECURITY;
ALTER TABLE threshold_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE excursion_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE shipment_logger_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE packaging_product_compatibilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_generation_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE validation_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE ground_truth_records ENABLE ROW LEVEL SECURITY;

-- Service Role Policies (Full access for backend service)
CREATE POLICY "service_role_all_packaging" ON packaging FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_products" ON products FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_lots" ON lots FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_shipments" ON shipments FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_loggers" ON loggers FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_readings" ON temperature_readings FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_custody" ON custody_events FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_stops" ON route_stops FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_policies" ON threshold_policies FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_excursions" ON excursion_reports FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_assignments" ON shipment_logger_assignments FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_compatibilities" ON packaging_product_compatibilities FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_compliance" ON compliance_reports FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_audit" ON audit_events FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_runs" ON data_generation_runs FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_validation" ON validation_results FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_roles" ON roles FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_users" ON users FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_ground_truth" ON ground_truth_records FOR ALL TO service_role USING (true) WITH CHECK (true);

-- Authenticated Users Policies
CREATE POLICY "auth_read_packaging" ON packaging FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_read_products" ON products FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_read_lots" ON lots FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_read_shipments" ON shipments FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_write_shipments" ON shipments FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "auth_update_shipments" ON shipments FOR UPDATE TO authenticated USING (true);
CREATE POLICY "auth_read_loggers" ON loggers FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_read_readings" ON temperature_readings FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_insert_readings" ON temperature_readings FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "auth_read_custody" ON custody_events FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_insert_custody" ON custody_events FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "auth_read_stops" ON route_stops FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_read_policies" ON threshold_policies FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_read_excursions" ON excursion_reports FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_update_excursions" ON excursion_reports FOR UPDATE TO authenticated USING (true);
CREATE POLICY "auth_read_compliance" ON compliance_reports FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_read_audit" ON audit_events FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_read_compatibilities" ON packaging_product_compatibilities FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_read_assignments" ON shipment_logger_assignments FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_read_runs" ON data_generation_runs FOR SELECT TO authenticated USING (true);
CREATE POLICY "auth_read_validation" ON validation_results FOR SELECT TO authenticated USING (true);

-- Anon Access Policies (Backend connection via SUPABASE_KEY during development)
CREATE POLICY "anon_all_packaging" ON packaging FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_products" ON products FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_lots" ON lots FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_shipments" ON shipments FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_loggers" ON loggers FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_readings" ON temperature_readings FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_custody" ON custody_events FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_stops" ON route_stops FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_policies" ON threshold_policies FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_excursions" ON excursion_reports FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_assignments" ON shipment_logger_assignments FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_compatibilities" ON packaging_product_compatibilities FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_compliance" ON compliance_reports FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_audit" ON audit_events FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_runs" ON data_generation_runs FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_validation" ON validation_results FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_roles" ON roles FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_all_users" ON users FOR ALL TO anon USING (true) WITH CHECK (true);
CREATE POLICY "anon_deny_ground_truth" ON ground_truth_records FOR SELECT TO anon USING (false);

-- ============================================================================
-- PART 8: INITIAL MASTER SEED DATA
-- ============================================================================

-- Roles
INSERT INTO roles (role_id, role_name, description) VALUES
('ROLE-01', 'Supplier', 'Biopharmaceutical supplier or contract manufacturing entity'),
('ROLE-02', 'Planner', 'Supply chain planner managing lots and dispatch scheduling'),
('ROLE-03', 'Carrier/Warehouse Operator', 'Freight carrier, 3PL handler, or cold storage operator'),
('ROLE-04', 'Logistics Analyst', 'Quality analyst reviewing excursions, missing data, and telemetry'),
('ROLE-05', 'Operations Manager', 'Operations manager authorizing release or quarantining shipments'),
('ROLE-06', 'Administrator', 'System administrator with full configuration permissions')
ON CONFLICT (role_id) DO NOTHING;

-- Users (Password: Admin@1234)
INSERT INTO users (user_id, email, password_hash, full_name, role, organization) VALUES
('USR-001', 'admin@coldchainiq.io', 'scrypt:32768:8:1$uH34i0yW8$a4bb56133be46b0a996f8c5b59ddb96ee31ee9db94aa0f00f07fa14d9b3a32f65a1ea03eb08e6ba2629b009e6c2cb9842f1cf8ba6e8ec9842a225da1ca12536b', 'System Administrator', 'Administrator', 'ColdChain IQ Global'),
('USR-002', 'analyst@coldchainiq.io', 'scrypt:32768:8:1$uH34i0yW8$a4bb56133be46b0a996f8c5b59ddb96ee31ee9db94aa0f00f07fa14d9b3a32f65a1ea03eb08e6ba2629b009e6c2cb9842f1cf8ba6e8ec9842a225da1ca12536b', 'Sarah Jenkins', 'Logistics Analyst', 'PharmaLogistics Inc'),
('USR-003', 'ops@coldchainiq.io', 'scrypt:32768:8:1$uH34i0yW8$a4bb56133be46b0a996f8c5b59ddb96ee31ee9db94aa0f00f07fa14d9b3a32f65a1ea03eb08e6ba2629b009e6c2cb9842f1cf8ba6e8ec9842a225da1ca12536b', 'Marcus Chen', 'Operations Manager', 'BioPharma Global Ops'),
('USR-004', 'planner@coldchainiq.io', 'scrypt:32768:8:1$uH34i0yW8$a4bb56133be46b0a996f8c5b59ddb96ee31ee9db94aa0f00f07fa14d9b3a32f65a1ea03eb08e6ba2629b009e6c2cb9842f1cf8ba6e8ec9842a225da1ca12536b', 'Elena Rossi', 'Planner', 'Supply Chain Solutions'),
('USR-005', 'carrier@coldchainiq.io', 'scrypt:32768:8:1$uH34i0yW8$a4bb56133be46b0a996f8c5b59ddb96ee31ee9db94aa0f00f07fa14d9b3a32f65a1ea03eb08e6ba2629b009e6c2cb9842f1cf8ba6e8ec9842a225da1ca12536b', 'David Vance', 'Carrier/Warehouse Operator', 'ColdTrans Freight Network')
ON CONFLICT (user_id) DO NOTHING;

-- Packaging
INSERT INTO packaging (packaging_id, packaging_name, packaging_type, minimum_temperature, maximum_temperature, validated_duration, insulation_type, status) VALUES
('PKG-001', 'AeroChill VIP Ultra 2-8C', 'VIP_CONTAINER', 2.00, 8.00, 96, 'VACUUM_INSULATED_PANEL', 'QUALIFIED'),
('PKG-002', 'CryoShipper DeepFreeze -80C', 'DRY_ICE_SHIPPER', -90.00, -60.00, 120, 'DRY_ICE_VACUUM', 'QUALIFIED'),
('PKG-003', 'BioShield Controlled Room 15-25C', 'GEL_PACK_BOX', 15.00, 25.00, 72, 'POLYURETHANE', 'QUALIFIED'),
('PKG-004', 'PolarGuard Active Reefer Unit', 'ACTIVE_REEFER', 2.00, 8.00, 168, 'EXPANDED_POLYSTYRENE', 'QUALIFIED'),
('PKG-005', 'CryoSafe Liquid Nitrogen Vapor', 'CRYOGENIC_DEWAR', -196.00, -150.00, 240, 'SUPER_INSULATION_JACKET', 'QUALIFIED')
ON CONFLICT (packaging_id) DO NOTHING;

-- Products
INSERT INTO products (product_id, product_name, product_category, minimum_temperature, maximum_temperature, allowed_excursion_duration, default_packaging_id, shelf_life_days, description, status) VALUES
('PROD-001', 'VaxiGuard mRNA Covid Booster', 'VACCINE_ULTRA_COLD', -80.00, -60.00, 30, 'PKG-002', 180, 'Lipid nanoparticle encapsulated mRNA vaccine requiring deep ultra-cold storage', 'ACTIVE'),
('PROD-002', 'InsuliPure Rapid Recombinant', 'INSULIN_BIOLOGIC', 2.00, 8.00, 60, 'PKG-001', 730, 'High-purity human insulin analog for diabetes management', 'ACTIVE'),
('PROD-003', 'OncoMab Monoclonal Antibody', 'MONOCLONAL_ANTIBODY', 2.00, 8.00, 45, 'PKG-001', 365, 'Targeted oncology immunotherapy biologic solution', 'ACTIVE'),
('PROD-004', 'ImmunoGlobulin IV High-Purity', 'BLOOD_DERIVED_PLASMA', 2.00, 8.00, 90, 'PKG-001', 540, 'Sterile intravenous immune globulin liquid formulation', 'ACTIVE'),
('PROD-005', 'RegenStem Autologous Cell Therapy', 'CELL_AND_GENE_THERAPY', -196.00, -150.00, 15, 'PKG-005', 90, 'Cryopreserved living cellular therapy for regenerative oncology', 'ACTIVE'),
('PROD-006', 'CardioPlatelet Platelet Rich Plasma', 'ROOM_TEMP_BLOOD_PRODUCT', 20.00, 24.00, 120, 'PKG-003', 7, 'Platelet suspension requiring gentle agitation and room temperature control', 'ACTIVE')
ON CONFLICT (product_id) DO NOTHING;

-- Packaging Product Compatibility
INSERT INTO packaging_product_compatibilities (id, product_id, packaging_id, qualified_status, max_transit_hours, validation_notes) VALUES
('COMPAT-001', 'PROD-001', 'PKG-002', 'QUALIFIED', 120, 'Validated for -80C dry ice transport up to 120h'),
('COMPAT-002', 'PROD-002', 'PKG-001', 'QUALIFIED', 96, 'Validated for 2-8C refrigerated transport up to 96h'),
('COMPAT-003', 'PROD-002', 'PKG-004', 'QUALIFIED', 168, 'Active reefer validated for long-haul reefer transit'),
('COMPAT-004', 'PROD-003', 'PKG-001', 'QUALIFIED', 96, 'Validated for 2-8C biologic transport'),
('COMPAT-005', 'PROD-004', 'PKG-001', 'QUALIFIED', 96, 'Validated for 2-8C IVIG liquid'),
('COMPAT-006', 'PROD-005', 'PKG-005', 'QUALIFIED', 240, 'Validated for liquid nitrogen dry shipper cryogenic'),
('COMPAT-007', 'PROD-006', 'PKG-003', 'QUALIFIED', 72, 'Validated for controlled room temperature 15-25C')
ON CONFLICT (id) DO NOTHING;

-- Threshold Policies
INSERT INTO threshold_policies (policy_id, product_id, minimum_temperature, maximum_temperature, allowed_excursion_duration, policy_version, policy_status) VALUES
('POL-2026-000001', 'PROD-001', -80.00, -60.00, 30, 'v1.0', 'ACTIVE'),
('POL-2026-000002', 'PROD-002', 2.00, 8.00, 60, 'v1.0', 'ACTIVE'),
('POL-2026-000003', 'PROD-003', 2.00, 8.00, 45, 'v1.0', 'ACTIVE'),
('POL-2026-000004', 'PROD-004', 2.00, 8.00, 90, 'v1.0', 'ACTIVE'),
('POL-2026-000005', 'PROD-005', -196.00, -150.00, 15, 'v1.0', 'ACTIVE'),
('POL-2026-000006', 'PROD-006', 20.00, 24.00, 120, 'v1.0', 'ACTIVE')
ON CONFLICT (policy_id) DO NOTHING;

-- Loggers
INSERT INTO loggers (logger_id, serial_number, model, calibration_date, calibration_expiry, accuracy_tolerance, measurement_uncertainty, battery_status, logger_status) VALUES
('LOG-2026-0001', 'SN-SENS-88401', 'Sensitech TempTale Ultra', NOW() - INTERVAL '30 days', NOW() + INTERVAL '335 days', 0.20, 0.10, 98.50, 'ACTIVE'),
('LOG-2026-0002', 'SN-SENS-88402', 'Sensitech TempTale Ultra', NOW() - INTERVAL '45 days', NOW() + INTERVAL '320 days', 0.20, 0.10, 96.00, 'ACTIVE'),
('LOG-2026-0003', 'SN-ELPRO-99201', 'Elpro Libero C-GLP', NOW() - INTERVAL '15 days', NOW() + INTERVAL '350 days', 0.15, 0.08, 99.00, 'ACTIVE'),
('LOG-2026-0004', 'SN-ELPRO-99202', 'Elpro Libero C-GLP', NOW() - INTERVAL '60 days', NOW() + INTERVAL '305 days', 0.15, 0.08, 92.00, 'ACTIVE'),
('LOG-2026-0005', 'SN-CRYO-77101', 'CryoBeacon LN2 Cryogenic', NOW() - INTERVAL '10 days', NOW() + INTERVAL '355 days', 0.50, 0.25, 100.00, 'ACTIVE')
ON CONFLICT (logger_id) DO NOTHING;
