# ColdChain IQ — Data Dictionary

## 1. Core Data Entities

### 1.1 `products`
| Column | Type | Nullable | Default | Description | Allowed Values / Validation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `product_id` | VARCHAR(64) | NO | - | Primary Key | Format: `PROD-001` |
| `product_name` | VARCHAR(255) | NO | - | Commercial brand name | e.g. "Comirnaty mRNA Vaccine" |
| `product_category` | VARCHAR(100) | NO | - | Product therapeutic class | `VACCINE`, `BIOLOGIC`, `INSULIN`, `CELL_THERAPY`, `BLOOD_PLASMA` |
| `minimum_temperature` | NUMERIC(5,2) | NO | - | Lower boundary (°C) | Must be < `maximum_temperature` |
| `maximum_temperature` | NUMERIC(5,2) | NO | - | Upper boundary (°C) | Must be > `minimum_temperature` |
| `allowed_excursion_duration`| INTEGER | NO | 0 | Max allowable out-of-spec mins | >= 0 |
| `default_packaging_id` | VARCHAR(64) | YES | NULL | FK to preferred packaging | Must exist in `packaging.packaging_id` |
| `shelf_life_days` | INTEGER | NO | - | Stability life in days | > 0 |
| `description` | TEXT | YES | NULL | Storage & handling guidance | Free text |
| `status` | VARCHAR(50) | NO | 'ACTIVE' | Lifecycle status | `ACTIVE`, `INACTIVE`, `DISCONTINUED` |
| `effective_from` | TIMESTAMPTZ | NO | NOW() | Effective start timestamp | ISO 8601 UTC |
| `effective_until` | TIMESTAMPTZ | YES | NULL | Expiration timestamp | Nullable or > `effective_from` |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Record creation audit | ISO 8601 UTC |
| `updated_at` | TIMESTAMPTZ | NO | NOW() | Record update audit | ISO 8601 UTC |

---

### 1.2 `lots`
| Column | Type | Nullable | Default | Description | Allowed Values / Validation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `lot_id` | VARCHAR(64) | NO | - | Primary Key | Format: `LOT-2026-000001` |
| `product_id` | VARCHAR(64) | NO | - | Foreign Key to `products` | Valid `product_id` |
| `supplier_name` | VARCHAR(255) | NO | - | Manufacturing organization | Non-empty string |
| `manufacturing_date` | DATE | NO | - | Release date | <= `expiry_date` |
| `expiry_date` | DATE | NO | - | Expiration date | > `manufacturing_date` |
| `quantity` | NUMERIC(12,2) | NO | - | Total quantity | > 0 |
| `unit` | VARCHAR(50) | NO | - | Unit of measurement | `VIALS`, `DOSES`, `PREFILLED_SYRINGES`, `KITS` |
| `lifecycle_status` | VARCHAR(50) | NO | 'RELEASED'| Release status | `RELEASED`, `QUARANTINED`, `REJECTED`, `EXPIRED` |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Record creation audit | ISO 8601 UTC |

---

### 1.3 `shipments`
| Column | Type | Nullable | Default | Description | Allowed Values / Validation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `shipment_id` | VARCHAR(64) | NO | - | Primary Key | Format: `SHP-2026-000001` |
| `lot_id` | VARCHAR(64) | NO | - | FK to `lots` | Valid `lot_id` |
| `product_id` | VARCHAR(64) | NO | - | FK to `products` | Valid `product_id`, must match lot's product |
| `packaging_id` | VARCHAR(64) | NO | - | FK to `packaging` | Valid `packaging_id` |
| `origin` | VARCHAR(255) | NO | - | Dispatch facility / city | e.g. "Basel Hub, Switzerland" |
| `destination` | VARCHAR(255) | NO | - | Consignee facility / city | e.g. "Boston Clinical Depot, USA" |
| `carrier_name` | VARCHAR(255) | NO | - | Logistics partner | e.g. "CryoExpress Global" |
| `planned_departure` | TIMESTAMPTZ | NO | - | Scheduled departure | ISO 8601 UTC |
| `actual_departure` | TIMESTAMPTZ | YES | NULL | Actual wheel-up timestamp | ISO 8601 UTC |
| `expected_arrival` | TIMESTAMPTZ | NO | - | Scheduled delivery | > `planned_departure` |
| `actual_arrival` | TIMESTAMPTZ | YES | NULL | Actual delivery timestamp | ISO 8601 UTC |
| `shipment_status` | VARCHAR(50) | NO | 'PLANNED' | Journey status | `PLANNED`, `IN_TRANSIT`, `DELIVERED`, `EXCEPTION`, `QUARANTINED` |
| `compliance_status` | VARCHAR(50) | NO | 'UNDER_REVIEW'| GxP decision | `COMPLIANT`, `NON_COMPLIANT`, `INCONCLUSIVE`, `UNDER_REVIEW` |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Audit timestamp | ISO 8601 UTC |

---

### 1.4 `loggers`
| Column | Type | Nullable | Default | Description | Allowed Values / Validation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `logger_id` | VARCHAR(64) | NO | - | Primary Key | Format: `LOG-2026-0001` |
| `serial_number` | VARCHAR(100) | NO | - | Hardware serial number | Unique string |
| `model` | VARCHAR(100) | NO | - | Device model | e.g. "Sensitech TempTale Ultra" |
| `calibration_date` | DATE | NO | - | NIST calibration issue | ISO Date |
| `calibration_expiry` | DATE | NO | - | NIST calibration expiry | > `calibration_date` |
| `accuracy_tolerance` | NUMERIC(4,2) | NO | 0.20 | Tolerance (°C) | >= 0 (e.g. ±0.20°C) |
| `measurement_uncertainty`| NUMERIC(4,2)| NO | 0.10 | Certified uncertainty (°C) | >= 0 (e.g. ±0.10°C) |
| `battery_status` | VARCHAR(50) | NO | 'GOOD' | Battery telemetry | `GOOD`, `LOW`, `CRITICAL` |
| `logger_status` | VARCHAR(50) | NO | 'ACTIVE' | Operational status | `ACTIVE`, `IN_USE`, `CALIBRATION_EXPIRED`, `DECOMMISSIONED` |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Audit timestamp | ISO 8601 UTC |

---

### 1.5 `temperature_readings`
| Column | Type | Nullable | Default | Description | Allowed Values / Validation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `reading_id` | VARCHAR(128)| NO | - | Primary Key | Format: `TEMP-<logger_id>-<timestamp>` |
| `logger_id` | VARCHAR(64) | NO | - | FK to `loggers` | Valid `logger_id` |
| `shipment_id` | VARCHAR(64) | NO | - | FK to `shipments` | Valid `shipment_id` |
| `recorded_at` | TIMESTAMPTZ | NO | - | Observation timestamp | Standard 10-minute intervals |
| `measured_temperature` | NUMERIC(5,2)| NO | - | Raw probe measurement (°C) | e.g. 4.85 |
| `corrected_temperature`| NUMERIC(5,2)| NO | - | NIST calibrated value (°C) | Raw adjusted for offset |
| `calibration_uncertainty`|NUMERIC(4,2)| NO | - | Certified uncertainty (°C) | Copied from logger certificate |
| `reading_status` | VARCHAR(50) | NO | 'VALID' | Telemetry evidence status | `VALID`, `UNASSIGNED_LOGGER`, `SUSPECT`, `CALIBRATION_INVALID` |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Ingestion timestamp | ISO 8601 UTC |

---

### 1.6 `custody_events`
| Column | Type | Nullable | Default | Description | Allowed Values / Validation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `custody_event_id` | VARCHAR(64) | NO | - | Primary Key | Format: `CUST-2026-000001` |
| `shipment_id` | VARCHAR(64) | NO | - | FK to `shipments` | Valid `shipment_id` |
| `previous_custodian` | VARCHAR(255) | NO | - | Releasing entity | Valid company / handler |
| `new_custodian` | VARCHAR(255) | NO | - | Receiving entity | Must match previous custodian on sequential handoff |
| `location` | VARCHAR(255) | NO | - | Transfer location | e.g. "Frankfurt Airport Ramp (FRA)" |
| `handoff_timestamp` | TIMESTAMPTZ | NO | - | Transfer timestamp | Sequential chronological order |
| `event_type` | VARCHAR(100) | NO | - | Type of custody transfer | `AIRPORT_RAMP_TRANSFER`, `WAREHOUSE_RECEIPT`, `LAST_MILE_DISPATCH` |
| `acknowledgement_status`| VARCHAR(50)| NO | 'ACKNOWLEDGED' | Signature state | `ACKNOWLEDGED`, `PENDING`, `DISPUTED` |
| `verification_status` | VARCHAR(50) | NO | 'VERIFIED' | Compliance state | `VERIFIED`, `CUSTODY_GAP`, `SIGNATURE_MISSING` |
| `notes` | TEXT | YES | NULL | Courier notes | Free text |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Audit timestamp | ISO 8601 UTC |

---

### 1.7 `excursion_reports`
| Column | Type | Nullable | Default | Description | Allowed Values / Validation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `excursion_id` | VARCHAR(64) | NO | - | Primary Key | Format: `EXCR-2026-000001` |
| `shipment_id` | VARCHAR(64) | NO | - | FK to `shipments` | Valid `shipment_id` |
| `product_id` | VARCHAR(64) | NO | - | FK to `products` | Valid `product_id` |
| `lot_id` | VARCHAR(64) | NO | - | FK to `lots` | Valid `lot_id` |
| `logger_id` | VARCHAR(64) | NO | - | FK to `loggers` | Valid `logger_id` |
| `start_timestamp` | TIMESTAMPTZ | NO | - | Excursion start | ISO 8601 UTC |
| `end_timestamp` | TIMESTAMPTZ | NO | - | Excursion end | >= `start_timestamp` |
| `calculated_duration` | INTEGER | NO | - | Cumulative minutes | Calculated strictly from valid readings |
| `minimum_observed_temperature`| NUMERIC(5,2)| NO | - | Min observed (°C) | Lowest temperature during event |
| `maximum_observed_temperature`| NUMERIC(5,2)| NO | - | Max observed (°C) | Highest temperature during event |
| `severity` | VARCHAR(50) | NO | - | Risk severity | `MINOR`, `MODERATE`, `CRITICAL` |
| `issue_type` | VARCHAR(100) | NO | - | Excursion classification | `UPPER_BOUND_EXCURSION`, `LOWER_BOUND_EXCURSION`, `TEMPERATURE_SPIKE` |
| `investigation_status` | VARCHAR(50) | NO | 'OPEN' | Workflow status | `OPEN`, `UNDER_REVIEW`, `RESOLVED`, `CLOSED` |
| `compliance_decision` | VARCHAR(50) | NO | - | QA disposition | `REVISE_HOLD`, `RELEASE`, `SCRAP_LOT` |
| `evidence_reference` | VARCHAR(255) | NO | - | Telemetry range ID | Traceable reading ID reference |
| `created_at` | TIMESTAMPTZ | NO | NOW() | Audit timestamp | ISO 8601 UTC |
