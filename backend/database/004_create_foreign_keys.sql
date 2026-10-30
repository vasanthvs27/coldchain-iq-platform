-- ============================================================================
-- 004_create_foreign_keys.sql
-- ColdChain IQ Platform: Foreign Keys & Referential Integrity
-- Validates, verifies, and documents all inter-table relationships.
-- ============================================================================

-- Table Documentation & Relationships
COMMENT ON TABLE products IS 'Master Product catalog with temperature thresholds';
COMMENT ON TABLE lots IS 'Manufactured batches associated 1:N with Products';
COMMENT ON TABLE shipments IS 'Transportation journeys associated with Lots, Products, and Packaging';
COMMENT ON TABLE packaging IS 'Thermal packaging units';
COMMENT ON TABLE loggers IS 'Physical IoT data loggers tracking temperature';
COMMENT ON TABLE temperature_readings IS 'Timestamped temperature readings linked to logger and shipment';
COMMENT ON TABLE custody_events IS 'Chain-of-custody transfer records along shipment route';
COMMENT ON TABLE route_stops IS 'Planned and actual transit stops with dwell calculation';
COMMENT ON TABLE threshold_policies IS 'Versioned temperature compliance threshold policies';
COMMENT ON TABLE excursion_reports IS 'Identified temperature excursion violations';
COMMENT ON TABLE shipment_logger_assignments IS 'History of logger assignments to shipments';
COMMENT ON TABLE packaging_product_compatibilities IS 'Compatibility matrix between packaging types and products';
COMMENT ON TABLE compliance_reports IS 'Formal evidence-backed compliance determination for shipments';
COMMENT ON TABLE ground_truth_records IS 'Isolated ground-truth benchmark labels for offline evaluation';

-- Optional: Ensure all foreign keys are created if tables existed previously without them
DO $$
BEGIN
    -- Ensure lots -> products foreign key
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_lots_product') THEN
        ALTER TABLE lots ADD CONSTRAINT fk_lots_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT;
    END IF;

    -- Ensure shipments -> lots foreign key
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_shipments_lot') THEN
        ALTER TABLE shipments ADD CONSTRAINT fk_shipments_lot FOREIGN KEY (lot_id) REFERENCES lots(lot_id) ON DELETE RESTRICT;
    END IF;

    -- Ensure shipments -> products foreign key
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_shipments_product') THEN
        ALTER TABLE shipments ADD CONSTRAINT fk_shipments_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT;
    END IF;

    -- Ensure shipments -> packaging foreign key
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_shipments_packaging') THEN
        ALTER TABLE shipments ADD CONSTRAINT fk_shipments_packaging FOREIGN KEY (packaging_id) REFERENCES packaging(packaging_id) ON DELETE RESTRICT;
    END IF;
END $$;
