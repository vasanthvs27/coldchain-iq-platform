# ColdChain IQ — Source Code Manifest

## 1. Inventory Summary

- **Total Backend Python Modules**: 35+
- **Total Frontend React Modules**: 28+
- **Total Database Schema Scripts**: 9
- **Total Test Suites**: 7 (50 test cases)
- **Total Documentation Files**: 13

---

## 2. Backend Module Manifest (`backend/`)

| File Path | Component Layer | Language | Purpose & Responsibilities |
| :--- | :--- | :--- | :--- |
| `run.py` | Server Entry | Python | Application entrypoint, binds Flask server to host & port. |
| `app/__init__.py` | Application Factory | Python | Initializes Flask app, registers blueprints under `/api/v1`, mounts Swagger UI. |
| `app/extensions.py` | Extensions | Python | Initializes `Flask-CORS` and `Flask-JWT-Extended`. |
| `app/config/__init__.py` | Configuration | Python | Global configuration, environment variable loader, JWT settings. |
| `app/config/supabase_client.py` | Database Client | Python | Centralized Supabase client with offline storage emulation fallback. |
| `app/utils/response.py` | Helpers | Python | Standardized JSON response formatting envelopes (`success`, `error`). |
| **Services (`app/services/`)** |
| `product_service.py` | Business Logic | Python | Product master data CRUD, temperature range validation ($T_{\min} < T_{\max}$). |
| `logger_service.py` | Business Logic | Python | NIST calibration validation, assignment history management. |
| `temperature_service.py` | Business Logic | Python | Ingestion, unassigned logger checks, 10-minute cadence telemetry gap detection. |
| `custody_service.py` | Business Logic | Python | Custody chain continuity verification and gap detection. |
| `excursion_service.py` | Business Logic | Python | Continuous excursion duration calculation, cross-shipment contamination isolation. |
| `compliance_service.py` | Business Logic | Python | 12-step deterministic compliance decision engine. |
| `generator_service.py` | Business Logic | Python | High-throughput synthetic data generator (Seed `20261022`, Starter & Full modes). |
| `validation_service.py` | Business Logic | Python | 3-tier validation (Structural, Business, Derived value reconciliation). |
| `evaluation_service.py` | Business Logic | Python | Offline evaluation, confusion matrix, Precision, Recall, F1 against ground truth. |
| `reproducibility_service.py`| Business Logic | Python | Dual-pass SHA-256 canonical dataset hashing and reproducibility verification. |
| `export_service.py` | Business Logic | Python | Chunked streaming export to CSV, JSON, SQL seed, and manifest generation. |
| `analytics_service.py` | Business Logic | Python | Platform KPI rollups, carrier risk scoring, route dwell aggregations. |
| **Routes (`app/routes/`)** |
| `health_routes.py` | API Layer | Python | Health check and readiness probes (`/api/v1/health`). |
| `auth_routes.py` | API Layer | Python | JWT authentication, user registration, role queries. |
| `dashboard_routes.py` | API Layer | Python | Executive summary KPIs, shipment trends, compliance distributions. |
| `product_routes.py` | API Layer | Python | Product endpoints, lot listings, policy listings. |
| `lot_routes.py` | API Layer | Python | Manufacturing lot batch management. |
| `shipment_routes.py` | API Layer | Python | Shipment dispatch, tracking, timeline, and sub-resource queries. |
| `packaging_routes.py` | API Layer | Python | Thermal packaging catalog and compatibility queries. |
| `logger_routes.py` | API Layer | Python | Logger catalog, assignment bindings, calibration tracking. |
| `temperature_routes.py` | API Layer | Python | Reading ingestion, time-series trends, telemetry gap detection. |
| `route_routes.py` | API Layer | Python | Route waypoints and dwell monitoring. |
| `custody_routes.py` | API Layer | Python | Custody event timeline and gap detection. |
| `policy_routes.py` | API Layer | Python | Threshold policy CRUD and product matching. |
| `excursion_routes.py` | API Layer | Python | Excursion investigations, root cause, and QA disposition. |
| `compliance_routes.py` | API Layer | Python | 12-step compliance evaluation trigger and certification export. |
| `analytics_routes.py` | API Layer | Python | Carrier risk, route dwell, and compliance breakdown. |
| `generator_routes.py` | API Layer | Python | Synthetic generation controls and status tracking. |
| `validation_routes.py` | API Layer | Python | Validation trigger and report retrieval. |
| `ground_truth_routes.py`| API Layer | Python | Ground truth evaluation metrics and confusion matrix. |
| `reproducibility_routes.py`| API Layer | Python | Dual-pass reproducibility verification run. |
| `audit_routes.py` | API Layer | Python | 21 CFR Part 11 append-only audit trail retrieval. |

---

## 3. Database Schema Scripts (`backend/database/`)

| Script Name | Purpose |
| :--- | :--- |
| `001_create_core_tables.sql` | Provisions all 10 core entities (products, lots, shipments, packaging, loggers, readings, etc.). |
| `002_create_supporting_tables.sql`| Provisions users, roles, bridge tables, compliance reports, audit events, validation results. |
| `003_create_relationships.sql` | Establishes all foreign-key relationships and cascade policies. |
| `004_create_indexes.sql` | Creates high-performance compound indexes for time-series telemetry. |
| `005_create_constraints.sql` | Enforces check constraints ($T_{\min} < T_{\max}$, positive quantities). |
| `006_create_functions.sql` | Stored procedures for telemetry duration calculations. |
| `007_create_triggers.sql` | Auto-updating timestamps and audit trail generation triggers. |
| `008_create_rls_policies.sql` | Row Level Security (RLS) policies for Supabase RBAC actors. |
| `009_seed_master_data.sql` | Baseline master data seed for initial deployment. |

---

## 4. Frontend Application Manifest (`frontend/src/`)

| File Path | Component Layer | Description |
| :--- | :--- | :--- |
| `main.jsx` | Entry | React DOM root mounting and StrictMode wrapper. |
| `App.jsx` | Router | React Router configuration for 22 application routes. |
| `index.css` | Styles | Tailwind CSS utility directives and custom scrollbars. |
| `services/api.js` | API Client | Central Axios instance with JWT interceptor and error envelope handler. |
| `services/supabaseClient.js` | Database Client | Official `@supabase/supabase-js` client instance. |
| `contexts/AuthContext.jsx` | State Context | User authentication context and 6-actor role switcher. |
| `layouts/DashboardLayout.jsx` | Layout | Enterprise dark-navy navigation sidebar, responsive top-bar, and user profile badge. |
| `components/common/` | UI Components | Reusable components: `PageHeader`, `StatCard`, `StatusBadge`. |
| `pages/Dashboard/` | Page | Executive KPI dashboard with interactive charts. |
| `pages/Shipments/` | Page | Shipment management with 8-tab inspection drawer and dispatch modal. |
| `pages/TemperatureMonitoring/`| Page | Interactive telemetry chart with threshold lines, excursion zones, and reading inspector. |
| `pages/Excursions/` | Page | Excursion investigation workspace with root cause logging. |
| `pages/ComplianceReports/` | Page | GxP compliance certificate viewer with JSON export. |
| `pages/RouteTracking/` | Page | Waypoint tracker and airport dwell time analysis. |
| `pages/CustodyEvents/` | Page | Chain-of-custody transfer timeline and gap flags. |
| `pages/Loggers/` | Page | Logger fleet monitor and assignment modal. |
| `pages/DataGaps/` | Page | Telemetry communication dropout inspector. |
| `pages/Calibration/` | Page | NIST calibration certification tracking. |
| `pages/Products/` | Page | Product catalog and temperature envelope specifications. |
| `pages/Lots/` | Page | Batch manufacturing release tracker. |
| `pages/Packaging/` | Page | Thermal packaging qualification catalog. |
| `pages/ThresholdPolicies/` | Page | Versioned temperature policy manager. |
| `pages/Analytics/` | Page | Fleet-wide analytics, carrier performance, and route trends. |
| `pages/RiskAssessment/` | Page | Risk scoring matrix and high-risk shipment flags. |
| `pages/DataGenerator/` | Page | Synthetic generator launcher (Seed `20261022`, Starter vs Full). |
| `pages/DataValidation/` | Page | 3-tier validation test dashboard. |
| `pages/GroundTruth/` | Page | Offline confusion matrix and precision/recall evaluation. |
| `pages/Reproducibility/` | Page | Dual-pass SHA-256 verification dashboard. |
| `pages/AuditTrail/` | Page | Immutable 21 CFR Part 11 event history viewer. |
| `pages/Settings/` | Page | Supabase configuration and system parameters. |
