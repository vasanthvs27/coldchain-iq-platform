# Supabase Database Schema Documentation

## 1. Overview & Setup Order

The ColdChain IQ database schema is implemented natively in Supabase PostgreSQL using 12 modular SQL scripts located in `backend/database/` (and consolidated in `docs/ALL_SUPABASE_QUERIES.sql`). To provision your Supabase database instance, execute the scripts sequentially in the **Supabase SQL Editor**:

```text
1. 001_extensions_and_types.sql       -> Extensions (uuid-ossp, pgcrypto)
2. 002_create_core_tables.sql         -> 10 Core Entities
3. 003_create_supporting_tables.sql   -> Roles, Users, Assignments, Compatibilities, Audit, etc.
4. 004_create_foreign_keys.sql        -> Foreign Key Constraints & Referential Documentation
5. 005_create_indexes.sql             -> High-Performance Indexes for Queries & Filtering
6. 006_create_constraints.sql         -> Check Constraints & Data Integrity Invariants
7. 007_create_functions.sql           -> Stored Procedures & Duration Calculation Functions
8. 008_create_triggers.sql            -> Automated Timestamp & Audit Trail Triggers
9. 009_enable_rls.sql                 -> Enable Row Level Security (RLS) on all 19 tables
10. 010_create_rls_policies.sql       -> Policies for Service Role, Authenticated, and Anon
11. 011_seed_master_data.sql          -> Baseline Products, Loggers, Packaging, Policies, Users
12. 012_verify_schema.sql             -> Complete Diagnostic Verification & Integrity Queries
```

*(Alternatively, you can run `docs/ALL_SUPABASE_QUERIES.sql` in a single execution.)*

---

## 2. Core Entities (10 Tables)

### 2.1 `products`
Defines pharmaceutical, biologic, and temperature-sensitive products.
- `product_id` (VARCHAR(64), PK): Unique deterministic ID (e.g. `PROD-001`).
- `product_name` (VARCHAR(255), NOT NULL): Commercial or clinical name.
- `product_category` (VARCHAR(100), NOT NULL): Category (e.g. `BIOLOGIC`, `VACCINE`, `INSULIN`, `CELL_THERAPY`).
- `minimum_temperature` (NUMERIC(5,2), NOT NULL): Lower temperature boundary in °C.
- `maximum_temperature` (NUMERIC(5,2), NOT NULL): Upper temperature boundary in °C.
- `allowed_excursion_duration` (INTEGER, NOT NULL): Maximum cumulative allowable excursion minutes before product compromise.
- `default_packaging_id` (VARCHAR(64), NULL): Default thermal packaging identifier.
- `shelf_life_days` (INTEGER, NOT NULL): Product shelf life in days.
- `description` (TEXT, NULL): Clinical/handling instructions.
- `status` (VARCHAR(50), NOT NULL DEFAULT 'ACTIVE'): `ACTIVE`, `INACTIVE`, `DISCONTINUED`.
- `effective_from` (TIMESTAMPTZ, NOT NULL): Start of validity period.
- `effective_until` (TIMESTAMPTZ, NULL): End of validity period.
- `created_at` (TIMESTAMPTZ, NOT NULL DEFAULT NOW()), `updated_at` (TIMESTAMPTZ, NOT NULL DEFAULT NOW()).

### 2.2 `lots`
Tracks manufactured batches associated with specific products.
- `lot_id` (VARCHAR(64), PK): Lot identifier (e.g. `LOT-2026-000001`).
- `product_id` (VARCHAR(64), NOT NULL, FK -> `products.product_id`).
- `supplier_name` (VARCHAR(255), NOT NULL): Origin manufacturer.
- `manufacturing_date` (DATE, NOT NULL): Date of manufacturing release.
- `expiry_date` (DATE, NOT NULL): Expiration date.
- `quantity` (NUMERIC(12,2), NOT NULL): Total batch count/volume.
- `unit` (VARCHAR(50), NOT NULL): Unit of measure (`VIALS`, `DOSES`, `PREFILLED_SYRINGES`).
- `lifecycle_status` (VARCHAR(50), NOT NULL DEFAULT 'RELEASED'): `RELEASED`, `QUARANTINED`, `REJECTED`, `EXPIRED`.
- `created_at` (TIMESTAMPTZ, NOT NULL DEFAULT NOW()).

### 2.3 `shipments`
Represents an individual transport journey of a lot from origin to destination.
- `shipment_id` (VARCHAR(64), PK): Identifier (e.g. `SHP-2026-000001`).
- `lot_id` (VARCHAR(64), NOT NULL, FK -> `lots.lot_id`).
- `product_id` (VARCHAR(64), NOT NULL, FK -> `products.product_id`).
- `packaging_id` (VARCHAR(64), NOT NULL, FK -> `packaging.packaging_id`).
- `origin` (VARCHAR(255), NOT NULL): Origin facility/city.
- `destination` (VARCHAR(255), NOT NULL): Destination clinical site/depot.
- `carrier_name` (VARCHAR(255), NOT NULL): Logistics provider (e.g. `CryoExpress Global`, `PolarLogistics`).
- `planned_departure` (TIMESTAMPTZ, NOT NULL), `actual_departure` (TIMESTAMPTZ, NULL).
- `expected_arrival` (TIMESTAMPTZ, NOT NULL), `actual_arrival` (TIMESTAMPTZ, NULL).
- `shipment_status` (VARCHAR(50), NOT NULL DEFAULT 'PLANNED'): `PLANNED`, `IN_TRANSIT`, `DELIVERED`, `EXCEPTION`, `QUARANTINED`.
- `compliance_status` (VARCHAR(50), NOT NULL DEFAULT 'UNDER_REVIEW'): `COMPLIANT`, `NON_COMPLIANT`, `INCONCLUSIVE`, `UNDER_REVIEW`.
- `created_at` (TIMESTAMPTZ, NOT NULL DEFAULT NOW()).

### 2.4 `packaging`
Thermal container and active refrigeration profiles.
- `packaging_id` (VARCHAR(64), PK): Identifier (e.g. `PKG-VIP-01`).
- `packaging_name` (VARCHAR(255), NOT NULL): Trade name (e.g. `AeroSafe VIP Shipper`).
- `packaging_type` (VARCHAR(100), NOT NULL): `PASSIVE_VIP`, `ACTIVE_COMPRESSOR`, `CRYOGENIC_DEWAR`.
- `minimum_temperature` (NUMERIC(5,2), NOT NULL): Min validated temperature.
- `maximum_temperature` (NUMERIC(5,2), NOT NULL): Max validated temperature.
- `validated_duration` (INTEGER, NOT NULL): Qualified thermal hold time in hours.
- `insulation_type` (VARCHAR(100), NOT NULL): e.g. `Vacuum Insulated Panel (VIP)`, `Dry Ice Sublimation`.
- `status` (VARCHAR(50), NOT NULL DEFAULT 'VALIDATED'): `VALIDATED`, `RETIRED`, `SUSPENDED`.

### 2.5 `loggers`
NIST-traceable electronic data loggers.
- `logger_id` (VARCHAR(64), PK): Deterministic ID (e.g. `LOG-2026-0001`).
- `serial_number` (VARCHAR(100), NOT NULL, UNIQUE): Manufacturer serial number.
- `model` (VARCHAR(100), NOT NULL): Hardware model (e.g. `Sensitech TempTale Ultra`, `Elpro Libero C-GLP`).
- `calibration_date` (DATE, NOT NULL): Last NIST calibration date.
- `calibration_expiry` (DATE, NOT NULL): Calibration expiration date.
- `accuracy_tolerance` (NUMERIC(4,2), NOT NULL): Sensor tolerance (e.g. `0.20` for ±0.2°C).
- `measurement_uncertainty` (NUMERIC(4,2), NOT NULL): Certified uncertainty (e.g. `0.10` for ±0.1°C).
- `battery_status` (VARCHAR(50), NOT NULL DEFAULT 'GOOD'): `GOOD`, `LOW`, `CRITICAL`.
- `logger_status` (VARCHAR(50), NOT NULL DEFAULT 'ACTIVE'): `ACTIVE`, `IN_USE`, `CALIBRATION_EXPIRED`, `DECOMMISSIONED`.
- `created_at` (TIMESTAMPTZ, NOT NULL DEFAULT NOW()).

### 2.6 `temperature_readings`
High-frequency timestamped sensor observations.
- `reading_id` (VARCHAR(128), PK): Unique ID (e.g. `TEMP-LOG-2026-0001-20261022T080000Z`).
- `logger_id` (VARCHAR(64), NOT NULL, FK -> `loggers.logger_id`).
- `shipment_id` (VARCHAR(64), NOT NULL, FK -> `shipments.shipment_id`).
- `recorded_at` (TIMESTAMPTZ, NOT NULL): Logger timestamp.
- `measured_temperature` (NUMERIC(5,2), NOT NULL): Raw sensor observation in °C.
- `corrected_temperature` (NUMERIC(5,2), NOT NULL): Temperature after applying calibration offset.
- `calibration_uncertainty` (NUMERIC(4,2), NOT NULL): Calibration uncertainty margin in °C.
- `reading_status` (VARCHAR(50), NOT NULL DEFAULT 'VALID'): `VALID`, `UNASSIGNED_LOGGER`, `SUSPECT`, `CALIBRATION_INVALID`.
- `created_at` (TIMESTAMPTZ, NOT NULL DEFAULT NOW()).

### 2.7 `custody_events`
Chain of custody and custody transfer records.
- `custody_event_id` (VARCHAR(64), PK): ID (e.g. `CUST-2026-000001`).
- `shipment_id` (VARCHAR(64), NOT NULL, FK -> `shipments.shipment_id`).
- `previous_custodian` (VARCHAR(255), NOT NULL): Releasing party.
- `new_custodian` (VARCHAR(255), NOT NULL): Receiving party.
- `location` (VARCHAR(255), NOT NULL): Physical handoff point.
- `handoff_timestamp` (TIMESTAMPTZ, NOT NULL): Time of transfer.
- `event_type` (VARCHAR(100), NOT NULL): `AIRPORT_RAMP_TRANSFER`, `WAREHOUSE_RECEIPT`, `LAST_MILE_DISPATCH`.
- `acknowledgement_status` (VARCHAR(50), NOT NULL DEFAULT 'ACKNOWLEDGED'): `ACKNOWLEDGED`, `PENDING`, `DISPUTED`.
- `verification_status` (VARCHAR(50), NOT NULL DEFAULT 'VERIFIED'): `VERIFIED`, `CUSTODY_GAP`, `SIGNATURE_MISSING`.
- `notes` (TEXT, NULL), `created_at` (TIMESTAMPTZ, NOT NULL DEFAULT NOW()).

### 2.8 `route_stops`
Transit waypoints, hubs, and airport dwell tracking.
- `route_stop_id` (VARCHAR(64), PK): ID (e.g. `STOP-2026-000001`).
- `shipment_id` (VARCHAR(64), NOT NULL, FK -> `shipments.shipment_id`).
- `stop_sequence` (INTEGER, NOT NULL): 1-indexed order of stops.
- `stop_name` (VARCHAR(255), NOT NULL): Facility name / IATA code.
- `stop_type` (VARCHAR(100), NOT NULL): `ORIGIN_DISPATCH`, `AIRPORT_HUB`, `CROSS_DOCK`, `CUSTOMS_BOND`, `FINAL_DESTINATION`.
- `planned_arrival` (TIMESTAMPTZ, NOT NULL), `actual_arrival` (TIMESTAMPTZ, NULL).
- `departure_time` (TIMESTAMPTZ, NULL).
- `dwell_duration` (INTEGER, NULL): Dwell duration in minutes.
- `status` (VARCHAR(50), NOT NULL DEFAULT 'SCHEDULED'): `SCHEDULED`, `ARRIVED`, `DEPARTED`, `DELAYED`.

### 2.9 `threshold_policies`
Effective temperature limits and regulatory profiles.
- `policy_id` (VARCHAR(64), PK): ID (e.g. `POL-2026-000001`).
- `product_id` (VARCHAR(64), NOT NULL, FK -> `products.product_id`).
- `minimum_temperature` (NUMERIC(5,2), NOT NULL): Lower limit in °C.
- `maximum_temperature` (NUMERIC(5,2), NOT NULL): Upper limit in °C.
- `allowed_excursion_duration` (INTEGER, NOT NULL): Permissible excursion minutes.
- `effective_from` (TIMESTAMPTZ, NOT NULL): Start date.
- `effective_until` (TIMESTAMPTZ, NULL): End date.
- `policy_version` (VARCHAR(50), NOT NULL): Semantic version (e.g. `v1.0`, `v2.1`).
- `policy_status` (VARCHAR(50), NOT NULL DEFAULT 'ACTIVE'): `ACTIVE`, `SUPERSEDED`, `DRAFT`.
- `created_at` (TIMESTAMPTZ, NOT NULL DEFAULT NOW()).

### 2.10 `excursion_reports`
Detailed records of thermal boundary violations.
- `excursion_id` (VARCHAR(64), PK): ID (e.g. `EXCR-2026-000001`).
- `shipment_id` (VARCHAR(64), NOT NULL, FK -> `shipments.shipment_id`).
- `product_id` (VARCHAR(64), NOT NULL, FK -> `products.product_id`).
- `lot_id` (VARCHAR(64), NOT NULL, FK -> `lots.lot_id`).
- `logger_id` (VARCHAR(64), NOT NULL, FK -> `loggers.logger_id`).
- `start_timestamp` (TIMESTAMPTZ, NOT NULL): Excursion onset.
- `end_timestamp` (TIMESTAMPTZ, NOT NULL): Excursion resolution.
- `calculated_duration` (INTEGER, NOT NULL): Cumulative duration in minutes.
- `minimum_observed_temperature` (NUMERIC(5,2), NOT NULL): Lowest reading during event.
- `maximum_observed_temperature` (NUMERIC(5,2), NOT NULL): Highest reading during event.
- `severity` (VARCHAR(50), NOT NULL): `MINOR`, `MODERATE`, `CRITICAL`.
- `issue_type` (VARCHAR(100), NOT NULL): `UPPER_BOUND_EXCURSION`, `LOWER_BOUND_EXCURSION`, `TEMPERATURE_SPIKE`.
- `investigation_status` (VARCHAR(50), NOT NULL DEFAULT 'OPEN'): `OPEN`, `UNDER_REVIEW`, `RESOLVED`, `CLOSED`.
- `compliance_decision` (VARCHAR(50), NOT NULL): `REVISE_HOLD`, `RELEASE`, `SCRAP_LOT`.
- `evidence_reference` (VARCHAR(255), NOT NULL): Traceable sensor reading ID range.
- `created_at` (TIMESTAMPTZ, NOT NULL DEFAULT NOW()).

---

## 3. Supporting Tables

- `users`: User profiles with `user_id`, `email`, `password_hash`, `role_id`, `full_name`, `status`.
- `roles`: Role definitions for 6 actors (`role_id`, `role_name`, `description`).
- `shipment_logger_assignments`: Historical bridge table linking loggers to shipments across specific time intervals (`assignment_id`, `shipment_id`, `logger_id`, `assigned_at`, `unassigned_at`, `status`).
- `packaging_product_compatibilities`: Matrix defining approved packaging systems for each product (`compatibility_id`, `packaging_id`, `product_id`, `is_preferred`).
- `compliance_reports`: Official GxP compliance decisions generated by the 12-step compliance engine (`report_id`, `shipment_id`, `final_decision`, `compliance_score`, `total_readings`, `valid_readings`, `missing_readings`, `excursion_count`, `reason_codes`, `evidence_references`, `evaluated_at`).
- `audit_events`: Tamper-evident 21 CFR Part 11 append-only log (`event_id`, `entity_type`, `entity_id`, `action`, `user_id`, `ip_address`, `old_values`, `new_values`, `created_at`).
- `data_generation_runs`: Run history for synthetic data generation (`run_id`, `seed`, `mode`, `shipment_count`, `status`, `started_at`, `completed_at`).
- `validation_results`: Validation run metrics and anomaly reports (`validation_id`, `rule_name`, `total_evaluated`, `passed_records`, `failed_records`, `expected_anomalies`, `unexpected_failures`, `affected_ids`, `validated_at`).

---

## 4. Database Constraints & Enforcements

1. **Product Temperature Logic**: `CHECK (minimum_temperature < maximum_temperature)` prevents nonsensical thermal thresholds.
2. **Reading Timestamps**: Index `idx_readings_shipment_time` on `(shipment_id, recorded_at ASC)` guarantees sub-millisecond retrieval of chronological sensor telemetry.
3. **Foreign Key Deletion Rules**: All foreign keys specify `ON DELETE RESTRICT` or `ON DELETE CASCADE` where appropriate, preventing orphan telemetry or cascade corruption.
4. **Primary Key Determinism**: Zero-padded immutable identifiers ensure uniqueness across synthetic generation passes.
