# ColdChain IQ — REST API Documentation

## 1. Overview & Protocol Standards

The ColdChain IQ REST API provides programmatic access to all temperature compliance, telemetric monitoring, master data, and analytical workflows.

- **Base URL**: `http://localhost:5000/api/v1`
- **Interactive Documentation**: OpenAPI / Swagger UI is available at `GET /api/v1/docs`.
- **Content Type**: `application/json`
- **Authentication**: Bearer Token in HTTP Authorization Header:
  ```http
  Authorization: Bearer <jwt_access_token>
  ```
- **Standard HTTP Response Envelopes**:
  - Success Response (200 OK / 201 Created):
    ```json
    {
      "success": true,
      "message": "Resource retrieved successfully",
      "data": { ... },
      "meta": { "total": 120, "page": 1, "limit": 25 }
    }
    ```
  - Error Response (400, 401, 403, 404, 409, 422, 500):
    ```json
    {
      "success": false,
      "message": "Product threshold mismatch",
      "error_code": "POLICY_MISMATCH",
      "details": {
        "shipment_id": "SHP-2026-000001",
        "expected_product": "PROD-001",
        "provided_product": "PROD-002"
      }
    }
    ```

---

## 2. API Endpoints Catalog

### 2.1 Authentication & RBAC (`/api/v1/auth`)
- `POST /api/v1/auth/login`: Authenticate using email and password. Returns JWT access token, user profile, and assigned roles.
- `POST /api/v1/auth/register`: Register a new user with email, password, full name, and initial actor role.
- `POST /api/v1/auth/refresh`: Refresh an expired access token using the refresh token.
- `POST /api/v1/auth/logout`: Revoke active JWT session.
- `GET /api/v1/auth/me`: Retrieve currently authenticated user context and active role permissions.

### 2.2 Executive Dashboard (`/api/v1/dashboard`)
- `GET /api/v1/dashboard/overview`: High-level summary of active shipments, compliance breakdown, open excursions, and active loggers.
- `GET /api/v1/dashboard/compliance-summary`: Breakdown of `COMPLIANT`, `NON_COMPLIANT`, `INCONCLUSIVE`, and `UNDER_REVIEW` counts.
- `GET /api/v1/dashboard/excursion-summary`: Total excursions categorized by severity (`MINOR`, `MODERATE`, `CRITICAL`) and issue type.
- `GET /api/v1/dashboard/shipment-trends`: 30-day historical time-series of dispatched vs. delivered shipments.
- `GET /api/v1/dashboard/temperature-trends`: System-wide average mean kinetic temperature (MKT) and ambient vs. payload delta.

### 2.3 Master Data (`/api/v1/products`, `/lots`, `/packaging`, `/loggers`)
- `GET /api/v1/products`: List all products (supports search, category filter, pagination).
- `POST /api/v1/products`: Register a new product with min/max temperature boundaries and shelf-life.
- `GET /api/v1/products/{product_id}`: Retrieve product details.
- `PUT /api/v1/products/{product_id}`: Update product specifications.
- `DELETE /api/v1/products/{product_id}`: Soft delete or retire product.
- `GET /api/v1/products/{product_id}/lots`: List all manufacturing lots manufactured for this product.
- `GET /api/v1/products/{product_id}/policies`: List all active and historical threshold policies for this product.
- `GET /api/v1/lots`: List all lots.
- `POST /api/v1/lots`: Register a new lot batch.
- `GET /api/v1/packaging`: List all thermal packaging types and qualification profiles.
- `GET /api/v1/loggers`: List all physical data loggers and their NIST calibration status.
- `POST /api/v1/loggers/{logger_id}/assign`: Assign a logger to an active shipment with assignment start timestamp.

### 2.4 Shipments & Operations (`/api/v1/shipments`)
- `GET /api/v1/shipments`: List shipments with query filters (`shipment_status`, `compliance_status`, `carrier_name`, `product_id`).
- `POST /api/v1/shipments`: Dispatch a new shipment linking lot, product, packaging, and route.
- `GET /api/v1/shipments/{shipment_id}`: Retrieve detailed shipment overview.
- `PUT /api/v1/shipments/{shipment_id}`: Update shipment status (e.g. mark `DELIVERED` or `QUARANTINED`).
- `GET /api/v1/shipments/{shipment_id}/timeline`: Retrieve combined chronological history of stops, custody handoffs, and reading milestones.
- `GET /api/v1/shipments/{shipment_id}/temperature`: Retrieve all temperature readings captured for this shipment.
- `GET /api/v1/shipments/{shipment_id}/custody`: Retrieve custody chain handoffs.
- `GET /api/v1/shipments/{shipment_id}/route`: Retrieve route waypoints and dwell durations.
- `GET /api/v1/shipments/{shipment_id}/excursions`: Retrieve all detected temperature excursions.
- `GET /api/v1/shipments/{shipment_id}/compliance`: Retrieve the 12-step compliance evaluation report.

### 2.5 Temperature Telemetry & Analysis (`/api/v1/temperature`)
- `GET /api/v1/temperature/readings`: Query telemetry readings with time-window and logger filters.
- `POST /api/v1/temperature/readings`: Ingest single or bulk temperature observations.
- `GET /api/v1/temperature/shipments/{shipment_id}/trends`: Aggregated telemetry series for charting.
- `GET /api/v1/temperature/shipments/{shipment_id}/gaps`: Detect missing intervals where gap > 10 minutes.
- `POST /api/v1/temperature/analyze`: Run ad-hoc temperature excursion analysis over arbitrary readings.

### 2.6 Excursion Investigation (`/api/v1/excursions`)
- `GET /api/v1/excursions`: List all excursions with severity and status filters.
- `GET /api/v1/excursions/{excursion_id}`: Retrieve full root-cause investigation dossier.
- `PUT /api/v1/excursions/{excursion_id}/investigation`: Submit investigation findings and QA disposition (`REVISE_HOLD`, `RELEASE`, `SCRAP_LOT`).
- `GET /api/v1/excursions/{excursion_id}/evidence`: Retrieve exact timestamped sensor readings proving the excursion.

### 2.7 Compliance Engine (`/api/v1/compliance`)
- `POST /api/v1/compliance/analyze/{shipment_id}`: Trigger full 12-step deterministic compliance engine for a shipment.
- `GET /api/v1/compliance/reports`: List all generated compliance certification records.
- `GET /api/v1/compliance/reports/{report_id}`: View certificate with reason codes and evidence references.
- `POST /api/v1/compliance/reports/{report_id}/export`: Export compliance certificate as formatted GxP PDF or JSON.

### 2.8 Synthetic Generator & Reproducibility (`/api/v1/generator`, `/reproducibility`)
- `POST /api/v1/generator/configure`: Set generator parameters (seed, shipment count, logger count, anomaly rates).
- `POST /api/v1/generator/run`: Start synthetic data generation (Starter Mode or Full 5,000-Shipment Mode).
- `GET /api/v1/generator/runs`: List historical generation runs.
- `GET /api/v1/generator/runs/{run_id}/status`: Track real-time background generation progress.
- `POST /api/v1/reproducibility/run`: Execute dual-pass generation with seed `20261022` and verify matching SHA-256 checksums.

### 2.9 Validation & Ground Truth Evaluation (`/api/v1/validation`, `/evaluation`)
- `POST /api/v1/validation/run`: Execute 3-tier validation (Structural, Business, Derived reconciliation).
- `GET /api/v1/validation/summary`: Retrieve validation pass/fail metrics.
- `POST /api/v1/evaluation/run`: Compare operational predictions against quarantined ground-truth labels.
- `GET /api/v1/evaluation/metrics`: Retrieve Precision, Recall, F1-Score, and Accuracy.
- `GET /api/v1/evaluation/confusion-matrix`: Retrieve TP, FP, TN, FN matrix across the 5 mandatory negative scenarios.
