-- ============================================================================
-- 006_create_constraints.sql
-- ColdChain IQ Platform: Check Constraints & Business Invariants
-- ============================================================================

DO $$
BEGIN
    -- 1. Product temperature bounds (min < max)
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_product_temp_range') THEN
        ALTER TABLE products ADD CONSTRAINT chk_product_temp_range CHECK (minimum_temperature < maximum_temperature);
    END IF;

    -- 2. Threshold policy temperature bounds (min < max)
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_policy_temp_range') THEN
        ALTER TABLE threshold_policies ADD CONSTRAINT chk_policy_temp_range CHECK (minimum_temperature < maximum_temperature);
    END IF;

    -- 3. Packaging temperature bounds (min < max)
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_packaging_temp_range') THEN
        ALTER TABLE packaging ADD CONSTRAINT chk_packaging_temp_range CHECK (minimum_temperature < maximum_temperature);
    END IF;

    -- 4. Route stop dwell duration non-negative
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_stop_dwell_nonneg') THEN
        ALTER TABLE route_stops ADD CONSTRAINT chk_stop_dwell_nonneg CHECK (dwell_duration >= 0);
    END IF;

    -- 5. Excursion duration non-negative & timestamp order
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_excursion_duration_nonneg') THEN
        ALTER TABLE excursion_reports ADD CONSTRAINT chk_excursion_duration_nonneg CHECK (calculated_duration >= 0);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_excursion_time_order') THEN
        ALTER TABLE excursion_reports ADD CONSTRAINT chk_excursion_time_order CHECK (start_timestamp <= end_timestamp);
    END IF;

    -- 6. Compliance score percentage bound [0, 100]
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_compliance_score_range') THEN
        ALTER TABLE compliance_reports ADD CONSTRAINT chk_compliance_score_range CHECK (compliance_score >= 0.00 AND compliance_score <= 100.00);
    END IF;
END $$;
