-- ============================================================================
-- 011_seed_master_data.sql
-- ColdChain IQ Platform: Initial Master Seed Data
-- ============================================================================

-- 1. Insert Roles
INSERT INTO roles (role_id, role_name, description) VALUES
('ROLE-01', 'Supplier', 'Biopharmaceutical supplier or contract manufacturing entity'),
('ROLE-02', 'Planner', 'Supply chain planner managing lots and dispatch scheduling'),
('ROLE-03', 'Carrier/Warehouse Operator', 'Freight carrier, 3PL handler, or cold storage operator'),
('ROLE-04', 'Logistics Analyst', 'Quality analyst reviewing excursions, missing data, and telemetry'),
('ROLE-05', 'Operations Manager', 'Operations manager authorizing release or quarantining shipments'),
('ROLE-06', 'Administrator', 'System administrator with full configuration permissions')
ON CONFLICT (role_id) DO NOTHING;

-- 2. Insert Users (Password: Admin@1234, precomputed hash)
INSERT INTO users (user_id, email, password_hash, full_name, role, organization) VALUES
('USR-001', 'admin@coldchainiq.io', 'scrypt:32768:8:1$uH34i0yW8$a4bb56133be46b0a996f8c5b59ddb96ee31ee9db94aa0f00f07fa14d9b3a32f65a1ea03eb08e6ba2629b009e6c2cb9842f1cf8ba6e8ec9842a225da1ca12536b', 'System Administrator', 'Administrator', 'ColdChain IQ Global'),
('USR-002', 'analyst@coldchainiq.io', 'scrypt:32768:8:1$uH34i0yW8$a4bb56133be46b0a996f8c5b59ddb96ee31ee9db94aa0f00f07fa14d9b3a32f65a1ea03eb08e6ba2629b009e6c2cb9842f1cf8ba6e8ec9842a225da1ca12536b', 'Sarah Jenkins', 'Logistics Analyst', 'PharmaLogistics Inc'),
('USR-003', 'ops@coldchainiq.io', 'scrypt:32768:8:1$uH34i0yW8$a4bb56133be46b0a996f8c5b59ddb96ee31ee9db94aa0f00f07fa14d9b3a32f65a1ea03eb08e6ba2629b009e6c2cb9842f1cf8ba6e8ec9842a225da1ca12536b', 'Marcus Chen', 'Operations Manager', 'BioPharma Global Ops'),
('USR-004', 'planner@coldchainiq.io', 'scrypt:32768:8:1$uH34i0yW8$a4bb56133be46b0a996f8c5b59ddb96ee31ee9db94aa0f00f07fa14d9b3a32f65a1ea03eb08e6ba2629b009e6c2cb9842f1cf8ba6e8ec9842a225da1ca12536b', 'Elena Rossi', 'Planner', 'Supply Chain Solutions'),
('USR-005', 'carrier@coldchainiq.io', 'scrypt:32768:8:1$uH34i0yW8$a4bb56133be46b0a996f8c5b59ddb96ee31ee9db94aa0f00f07fa14d9b3a32f65a1ea03eb08e6ba2629b009e6c2cb9842f1cf8ba6e8ec9842a225da1ca12536b', 'David Vance', 'Carrier/Warehouse Operator', 'ColdTrans Freight Network')
ON CONFLICT (user_id) DO NOTHING;

-- 3. Insert Thermal Packaging Units
INSERT INTO packaging (packaging_id, packaging_name, packaging_type, minimum_temperature, maximum_temperature, validated_duration, insulation_type, status) VALUES
('PKG-001', 'AeroChill VIP Ultra 2-8C', 'VIP_CONTAINER', 2.00, 8.00, 96, 'VACUUM_INSULATED_PANEL', 'QUALIFIED'),
('PKG-002', 'CryoShipper DeepFreeze -80C', 'DRY_ICE_SHIPPER', -90.00, -60.00, 120, 'DRY_ICE_VACUUM', 'QUALIFIED'),
('PKG-003', 'BioShield Controlled Room 15-25C', 'GEL_PACK_BOX', 15.00, 25.00, 72, 'POLYURETHANE', 'QUALIFIED'),
('PKG-004', 'PolarGuard Active Reefer Unit', 'ACTIVE_REEFER', 2.00, 8.00, 168, 'EXPANDED_POLYSTYRENE', 'QUALIFIED'),
('PKG-005', 'CryoSafe Liquid Nitrogen Vapor', 'CRYOGENIC_DEWAR', -196.00, -150.00, 240, 'SUPER_INSULATION_JACKET', 'QUALIFIED')
ON CONFLICT (packaging_id) DO NOTHING;

-- 4. Insert Products
INSERT INTO products (product_id, product_name, product_category, minimum_temperature, maximum_temperature, allowed_excursion_duration, default_packaging_id, shelf_life_days, description, status) VALUES
('PROD-001', 'VaxiGuard mRNA Covid Booster', 'VACCINE_ULTRA_COLD', -80.00, -60.00, 30, 'PKG-002', 180, 'Lipid nanoparticle encapsulated mRNA vaccine requiring deep ultra-cold storage', 'ACTIVE'),
('PROD-002', 'InsuliPure Rapid Recombinant', 'INSULIN_BIOLOGIC', 2.00, 8.00, 60, 'PKG-001', 730, 'High-purity human insulin analog for diabetes management', 'ACTIVE'),
('PROD-003', 'OncoMab Monoclonal Antibody', 'MONOCLONAL_ANTIBODY', 2.00, 8.00, 45, 'PKG-001', 365, 'Targeted oncology immunotherapy biologic solution', 'ACTIVE'),
('PROD-004', 'ImmunoGlobulin IV High-Purity', 'BLOOD_DERIVED_PLASMA', 2.00, 8.00, 90, 'PKG-001', 540, 'Sterile intravenous immune globulin liquid formulation', 'ACTIVE'),
('PROD-005', 'RegenStem Autologous Cell Therapy', 'CELL_AND_GENE_THERAPY', -196.00, -150.00, 15, 'PKG-005', 90, 'Cryopreserved living cellular therapy for regenerative oncology', 'ACTIVE'),
('PROD-006', 'CardioPlatelet Platelet Rich Plasma', 'ROOM_TEMP_BLOOD_PRODUCT', 20.00, 24.00, 120, 'PKG-003', 7, 'Platelet suspension requiring gentle agitation and room temperature control', 'ACTIVE')
ON CONFLICT (product_id) DO NOTHING;

-- 5. Insert Packaging Product Compatibilities
INSERT INTO packaging_product_compatibilities (id, product_id, packaging_id, qualified_status, max_transit_hours, validation_notes) VALUES
('COMPAT-001', 'PROD-001', 'PKG-002', 'QUALIFIED', 120, 'Validated for -80C dry ice transport up to 120h'),
('COMPAT-002', 'PROD-002', 'PKG-001', 'QUALIFIED', 96, 'Validated for 2-8C refrigerated transport up to 96h'),
('COMPAT-003', 'PROD-002', 'PKG-004', 'QUALIFIED', 168, 'Active reefer validated for long-haul reefer transit'),
('COMPAT-004', 'PROD-003', 'PKG-001', 'QUALIFIED', 96, 'Validated for 2-8C biologic transport'),
('COMPAT-005', 'PROD-004', 'PKG-001', 'QUALIFIED', 96, 'Validated for 2-8C IVIG liquid'),
('COMPAT-006', 'PROD-005', 'PKG-005', 'QUALIFIED', 240, 'Validated for liquid nitrogen dry shipper cryogenic'),
('COMPAT-007', 'PROD-006', 'PKG-003', 'QUALIFIED', 72, 'Validated for controlled room temperature 15-25C')
ON CONFLICT (id) DO NOTHING;

-- 6. Insert Threshold Policies
INSERT INTO threshold_policies (policy_id, product_id, minimum_temperature, maximum_temperature, allowed_excursion_duration, policy_version, policy_status) VALUES
('POL-2026-000001', 'PROD-001', -80.00, -60.00, 30, 'v1.0', 'ACTIVE'),
('POL-2026-000002', 'PROD-002', 2.00, 8.00, 60, 'v1.0', 'ACTIVE'),
('POL-2026-000003', 'PROD-003', 2.00, 8.00, 45, 'v1.0', 'ACTIVE'),
('POL-2026-000004', 'PROD-004', 2.00, 8.00, 90, 'v1.0', 'ACTIVE'),
('POL-2026-000005', 'PROD-005', -196.00, -150.00, 15, 'v1.0', 'ACTIVE'),
('POL-2026-000006', 'PROD-006', 20.00, 24.00, 120, 'v1.0', 'ACTIVE')
ON CONFLICT (policy_id) DO NOTHING;

-- 7. Insert Initial NIST-Calibrated Loggers
INSERT INTO loggers (logger_id, serial_number, model, calibration_date, calibration_expiry, accuracy_tolerance, measurement_uncertainty, battery_status, logger_status) VALUES
('LOG-2026-0001', 'SN-SENS-88401', 'Sensitech TempTale Ultra', NOW() - INTERVAL '30 days', NOW() + INTERVAL '335 days', 0.20, 0.10, 98.50, 'ACTIVE'),
('LOG-2026-0002', 'SN-SENS-88402', 'Sensitech TempTale Ultra', NOW() - INTERVAL '45 days', NOW() + INTERVAL '320 days', 0.20, 0.10, 96.00, 'ACTIVE'),
('LOG-2026-0003', 'SN-ELPRO-99201', 'Elpro Libero C-GLP', NOW() - INTERVAL '15 days', NOW() + INTERVAL '350 days', 0.15, 0.08, 99.00, 'ACTIVE'),
('LOG-2026-0004', 'SN-ELPRO-99202', 'Elpro Libero C-GLP', NOW() - INTERVAL '60 days', NOW() + INTERVAL '305 days', 0.15, 0.08, 92.00, 'ACTIVE'),
('LOG-2026-0005', 'SN-CRYO-77101', 'CryoBeacon LN2 Cryogenic', NOW() - INTERVAL '10 days', NOW() + INTERVAL '355 days', 0.50, 0.25, 100.00, 'ACTIVE')
ON CONFLICT (logger_id) DO NOTHING;
