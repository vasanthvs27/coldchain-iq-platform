# ColdChain IQ — Supabase Database Integration & SQL Deployment Guide

## 1. Executive Summary

This guide provides the exact SQL scripts, execution order, and configuration instructions to deploy the complete **ColdChain IQ** database schema directly into your managed **Supabase PostgreSQL** project.

- **Supabase Project URL**: `https://mfndmbxxqruwfuuwkxyl.supabase.co`
- **Database Engine**: PostgreSQL 15 (Supabase Managed)
- **Architecture**: React Frontend → Flask REST API → Supabase Python SDK (`supabase`) → Supabase PostgreSQL Database

---

## 2. Where to Execute the SQL Queries

1. Open your browser and log in to [Supabase Management Console](https://supabase.com/dashboard).
2. Open your project: **ColdChain IQ** (`mfndmbxxqruwfuuwkxyl`).
3. In the left navigation menu, click on the **SQL Editor** icon (represented by `>_`).
4. Click **New Query** (or the **+** button).
5. You can execute the queries in one of two ways:
   - **Method A (Recommended: One-Click Master Script)**: Copy and paste the entire contents of [`docs/ALL_SUPABASE_QUERIES.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/docs/ALL_SUPABASE_QUERIES.sql) into the SQL Editor and click **Run**.
   - **Method B (Modular Execution)**: Execute the 12 numbered SQL files from `backend/database/` sequentially.

---

## 3. Modular SQL Execution Sequence

Execute the following 12 files in exact numerical order:

| Step | Script File | Target Objects |
| :---: | :--- | :--- |
| **01** | [`001_extensions_and_types.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/001_extensions_and_types.sql) | Enables `uuid-ossp` and `pgcrypto` extensions. |
| **02** | [`002_create_core_tables.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/002_create_core_tables.sql) | Creates the 10 core entities (`packaging`, `products`, `lots`, `shipments`, `loggers`, `temperature_readings`, `custody_events`, `route_stops`, `threshold_policies`, `excursion_reports`). |
| **03** | [`003_create_supporting_tables.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/003_create_supporting_tables.sql) | Creates supporting tables: `roles`, `users`, `shipment_logger_assignments`, `packaging_product_compatibilities`, `compliance_reports`, `audit_events`, `data_generation_runs`, `validation_results`, `ground_truth_records`. |
| **04** | [`004_create_foreign_keys.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/004_create_foreign_keys.sql) | Establishes and verifies all referential constraints and table documentation. |
| **05** | [`005_create_indexes.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/005_create_indexes.sql) | Provisions high-performance indexes for time-series telemetry and query filtering. |
| **06** | [`006_create_constraints.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/006_create_constraints.sql) | Adds check constraints (`min_temp < max_temp`, positive quantities, non-negative durations). |
| **07** | [`007_create_functions.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/007_create_functions.sql) | Stored procedures for `updated_at`, duration calculations, and logger assignment checks. |
| **08** | [`008_create_triggers.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/008_create_triggers.sql) | Creates automated timestamp triggers for `products` and `users`. |
| **09** | [`009_enable_rls.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/009_enable_rls.sql) | Enables Row Level Security (RLS) across all 19 application tables. |
| **10** | [`010_create_rls_policies.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/010_create_rls_policies.sql) | Provisions security policies for `service_role`, `authenticated`, and `anon` roles. |
| **11** | [`011_seed_master_data.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/011_seed_master_data.sql) | Populates master seed data (Roles, Users, Packaging, Products, Compatibility, Policies, Initial Loggers). |
| **12** | [`012_verify_schema.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/012_verify_schema.sql) | Runs comprehensive diagnostic queries verifying tables, columns, indexes, policies, and row counts. |

---

## 4. Verification in Supabase SQL Editor

After executing the scripts, run the queries in [`012_verify_schema.sql`](file:///d:/vs/COLDCHAIN%20IQ%20PLATFORM/backend/database/012_verify_schema.sql).

### Expected Results
1. **Tables**: 19 tables + 1 view listed with status `BASE TABLE (OK)` or `VIEW (OK)`.
2. **Primary Keys**: Every table has its defined primary key (`product_id`, `lot_id`, `shipment_id`, etc.).
3. **Foreign Keys**: All parent-child relationships (`lots -> products`, `shipments -> lots`, etc.) are established.
4. **Row Level Security**: `rls_enabled` is `true` for all tables.
5. **Master Seed Rows**:
   - `products`: 6 rows
   - `packaging`: 5 rows
   - `threshold_policies`: 6 rows
   - `roles`: 6 rows
   - `users`: 5 rows
   - `packaging_product_compatibilities`: 7 rows
   - `loggers`: 5 rows
6. **Diagnostics**: Zero orphan lots, zero product/lot mismatches, and zero unassigned readings.

---

## 5. Security & Service Role Key Recommendation

In Supabase, two API keys are provided:
1. **`anon` / Public Key**: Used for public client access.
2. **`service_role` / Secret Key**: Bypasses Row Level Security (RLS). Used only inside trusted backend servers.

> **Important Note for Production**:  
> In your `backend/.env`, set `SUPABASE_SERVICE_ROLE_KEY` with your secret key from **Supabase Dashboard -> Project Settings -> API -> `service_role` (secret)**.  
> This allows the backend to perform privileged bulk ingestion, compliance scoring, and system maintenance without RLS restrictions, while Flask enforces all business logic, authentication, and role authorization.
