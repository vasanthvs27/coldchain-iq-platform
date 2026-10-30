-- ============================================================================
-- 010_create_rls_policies.sql
-- ColdChain IQ Platform: Row Level Security Policies
-- Designed for:
--  1. Service Role (Full privileged backend access)
--  2. Authenticated Users (Role-based access)
--  3. Anon Key (Safe development & backend gateway operations)
--  4. Ground Truth Isolation (Quarantined from public operational queries)
-- ============================================================================

-- Drop existing policies if previously applied to ensure idempotency
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (
        SELECT policyname, tablename 
        FROM pg_policies 
        WHERE schemaname = 'public'
    ) LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I', r.policyname, r.tablename);
    END LOOP;
END $$;

-- ----------------------------------------------------------------------------
-- 1. SERVICE ROLE POLICIES (Full unconstrained access for backend operations)
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- 2. AUTHENTICATED USER POLICIES (Read & Operational workflows)
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- 3. ANON ACCESS POLICIES (Backend API Gateway & Development Access)
-- Allows the Flask backend to query and persist data when connected using SUPABASE_KEY.
-- ----------------------------------------------------------------------------
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

-- Ground truth evaluation is strictly protected from anon:
CREATE POLICY "anon_deny_ground_truth" ON ground_truth_records FOR SELECT TO anon USING (false);
