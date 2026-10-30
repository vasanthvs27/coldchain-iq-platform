-- ============================================================================
-- 002_create_core_tables.sql
-- ColdChain IQ Platform: 10 Core Entities
-- Tables are created in dependency-safe order.
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
    dwell_duration INTEGER NOT NULL DEFAULT 0, -- dwell duration in minutes
    status VARCHAR(32) NOT NULL DEFAULT 'COMPLETED'
);

-- 9. Threshold Policies Table
CREATE TABLE IF NOT EXISTS threshold_policies (
    policy_id VARCHAR(64) PRIMARY KEY,
    product_id VARCHAR(64) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    minimum_temperature NUMERIC(5, 2) NOT NULL,
    maximum_temperature NUMERIC(5, 2) NOT NULL,
    allowed_excursion_duration INTEGER NOT NULL DEFAULT 60, -- minutes
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
    calculated_duration INTEGER NOT NULL, -- minutes
    minimum_observed_temperature NUMERIC(5, 2) NOT NULL,
    maximum_observed_temperature NUMERIC(5, 2) NOT NULL,
    severity VARCHAR(32) NOT NULL DEFAULT 'MEDIUM',
    issue_type VARCHAR(64) NOT NULL,
    investigation_status VARCHAR(32) NOT NULL DEFAULT 'OPEN',
    compliance_decision VARCHAR(32) NOT NULL DEFAULT 'UNDER_REVIEW',
    evidence_reference TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
