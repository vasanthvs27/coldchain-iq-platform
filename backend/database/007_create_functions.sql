-- ============================================================================
-- 007_create_functions.sql
-- ColdChain IQ Platform: Stored Procedures & Duration Calculators
-- ============================================================================

-- 1. Automatic updated_at timestamp trigger function
CREATE OR REPLACE FUNCTION set_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. Stored function to verify logger assignment validity
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

-- 3. Stored function to calculate cumulative excursion duration in minutes
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
