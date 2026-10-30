-- ============================================================================
-- 005_create_indexes.sql
-- ColdChain IQ Platform: High-Performance Database Indexes
-- Optimized for time-series telemetry, status lookups, and audit trails.
-- ============================================================================

-- 1. Shipments
CREATE INDEX IF NOT EXISTS idx_shipments_product_id ON shipments(product_id);
CREATE INDEX IF NOT EXISTS idx_shipments_lot_id ON shipments(lot_id);
CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(shipment_status);
CREATE INDEX IF NOT EXISTS idx_shipments_compliance ON shipments(compliance_status);
CREATE INDEX IF NOT EXISTS idx_shipments_planned_departure ON shipments(planned_departure);

-- 2. Temperature Readings (Optimized for 5,000 shipments & 500k+ readings)
CREATE INDEX IF NOT EXISTS idx_temp_readings_shipment ON temperature_readings(shipment_id);
CREATE INDEX IF NOT EXISTS idx_temp_readings_logger ON temperature_readings(logger_id);
CREATE INDEX IF NOT EXISTS idx_temp_readings_recorded_at ON temperature_readings(recorded_at);
CREATE INDEX IF NOT EXISTS idx_temp_readings_shipment_time ON temperature_readings(shipment_id, recorded_at ASC);
CREATE INDEX IF NOT EXISTS idx_temp_readings_status ON temperature_readings(reading_status);

-- 3. Custody Events
CREATE INDEX IF NOT EXISTS idx_custody_shipment ON custody_events(shipment_id);
CREATE INDEX IF NOT EXISTS idx_custody_timestamp ON custody_events(handoff_timestamp ASC);

-- 4. Route Stops
CREATE INDEX IF NOT EXISTS idx_route_stops_shipment ON route_stops(shipment_id);
CREATE INDEX IF NOT EXISTS idx_route_stops_sequence ON route_stops(shipment_id, stop_sequence ASC);

-- 5. Excursion Reports
CREATE INDEX IF NOT EXISTS idx_excursions_shipment ON excursion_reports(shipment_id);
CREATE INDEX IF NOT EXISTS idx_excursions_severity ON excursion_reports(severity);
CREATE INDEX IF NOT EXISTS idx_excursions_status ON excursion_reports(investigation_status);

-- 6. Threshold Policies
CREATE INDEX IF NOT EXISTS idx_policies_product ON threshold_policies(product_id);
CREATE INDEX IF NOT EXISTS idx_policies_status ON threshold_policies(policy_status);

-- 7. Shipment Logger Assignments
CREATE INDEX IF NOT EXISTS idx_assignments_shipment_logger ON shipment_logger_assignments(shipment_id, logger_id);
CREATE INDEX IF NOT EXISTS idx_assignments_dates ON shipment_logger_assignments(assigned_at, unassigned_at);

-- 8. Compliance Reports
CREATE INDEX IF NOT EXISTS idx_compliance_reports_shipment ON compliance_reports(shipment_id);
CREATE INDEX IF NOT EXISTS idx_compliance_reports_status ON compliance_reports(compliance_status);

-- 9. Audit Events
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_events(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_events(created_at DESC);

-- 10. Ground Truth Records
CREATE INDEX IF NOT EXISTS idx_ground_truth_entity ON ground_truth_records(entity_id);
CREATE INDEX IF NOT EXISTS idx_ground_truth_type ON ground_truth_records(issue_type);
