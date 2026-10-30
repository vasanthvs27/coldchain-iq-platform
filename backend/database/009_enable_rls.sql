-- ============================================================================
-- 009_enable_rls.sql
-- ColdChain IQ Platform: Enable Row Level Security (RLS) on all tables
-- ============================================================================

-- Core Tables
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

-- Supporting Tables
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE shipment_logger_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE packaging_product_compatibilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_generation_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE validation_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE ground_truth_records ENABLE ROW LEVEL SECURITY;
