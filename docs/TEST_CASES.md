# ColdChain IQ — Complete Test Cases Matrix (TC01 – TC50)

## 1. Test Execution Summary

- **Total Automated Test Cases**: 50
- **Passed**: 50 (100%)
- **Failed**: 0 (0%)
- **Execution Engine**: Pytest 9.2.0 on Python 3.13.1
- **Test Command**: `pytest -v`
- **Total Execution Duration**: 3.51 seconds

---

## 2. Detailed Test Catalog

### Group A — Master Data Management (TC01 – TC08)

| Test ID | Title | Input Parameters | Expected Result | Actual Result | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC01** | Product creation | `product_id="PROD-TEST"`, min=2.0°C, max=8.0°C | Product created successfully with status `ACTIVE` | Created with ID `PROD-TEST` | **PASS** | `test_master_data.py::test_tc01_product_creation` |
| **TC02** | Invalid product temperature range | min=8.0°C, max=2.0°C ($T_{\min} \ge T_{\max}$) | Rejection with `ValueError` | Rejected: `min_temp must be < max_temp` | **PASS** | `test_master_data.py::test_tc02_invalid_product_temperature_range` |
| **TC03** | Lot creation | `lot_id="LOT-TEST-001"`, `product_id="PROD-001"` | Lot registered with `RELEASED` status | Lot created successfully | **PASS** | `test_master_data.py::test_tc03_lot_creation` |
| **TC04** | Invalid lot-product relationship | `product_id="PROD-NONEXISTENT"` | Foreign key violation / missing product error | Rejected: `Product does not exist` | **PASS** | `test_master_data.py::test_tc04_invalid_lot_product_relationship` |
| **TC05** | Shipment creation | Valid lot, product, packaging, origin, destination | Shipment registered with `PLANNED` status | Shipment created with ID `SHP-TEST-001` | **PASS** | `test_master_data.py::test_tc05_shipment_creation` |
| **TC06** | Invalid shipment-lot relationship | `lot_id="LOT-NONEXISTENT"` | Rejection: Lot does not exist | Rejected: `Lot does not exist` | **PASS** | `test_master_data.py::test_tc06_invalid_shipment_lot_relationship` |
| **TC07** | Packaging compatibility | Product `PROD-001`, Packaging `PKG-VIP-01` | Compatibility confirmed in bridge table | Valid compatibility confirmed | **PASS** | `test_master_data.py::test_tc07_packaging_compatibility` |
| **TC08** | Logger assignment | Logger `LOG-TEST-01` assigned to `SHP-TEST-001` | Assignment created with timestamp window | Assignment active in `shipment_logger_assignments` | **PASS** | `test_master_data.py::test_tc08_logger_assignment` |

---

### Group B — Temperature Telemetry & Sensing (TC09 – TC16)

| Test ID | Title | Input Parameters | Expected Result | Actual Result | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC09** | Normal temperature reading | Temp = 4.5°C for 2.0°C to 8.0°C product | Marked `VALID`, zero excursions | Marked `VALID`, excursion duration = 0 mins | **PASS** | `test_temperature.py::test_tc09_normal_temperature_reading` |
| **TC10** | Upper temperature excursion | Temp = 9.8°C (above 8.0°C limit) | Excursion flagged with severity `MODERATE` | Flagged: `UPPER_BOUND_EXCURSION` | **PASS** | `test_temperature.py::test_tc10_upper_temperature_excursion` |
| **TC11** | Lower temperature excursion | Temp = 0.5°C (below 2.0°C limit) | Excursion flagged with severity `CRITICAL` | Flagged: `LOWER_BOUND_EXCURSION` | **PASS** | `test_temperature.py::test_tc11_lower_temperature_excursion` |
| **TC12** | Allowed excursion duration | Cumulative out-of-spec = 20 mins, allowed = 30 mins | Excursion recorded, within threshold | Status maintained within allowed threshold | **PASS** | `test_temperature.py::test_tc12_allowed_excursion_duration` |
| **TC13** | Excursion exceeding allowed duration | Cumulative out-of-spec = 60 mins, allowed = 30 mins | Shipment marked `NON_COMPLIANT` | Marked `NON_COMPLIANT` with reason code | **PASS** | `test_temperature.py::test_tc13_excursion_exceeding_allowed_duration` |
| **TC14** | Calibration uncertainty | Raw = 7.9°C, offset = +0.2°C, corrected = 8.1°C | Corrected temperature exceeds 8.0°C | Excursion triggered on corrected value | **PASS** | `test_temperature.py::test_tc14_calibration_uncertainty` |
| **TC15** | Missing reading detection | Readings separated by 40 mins (cadence = 10 mins) | Flagged as telemetry gap of 3 missing readings | Gap detected: 3 missing intervals | **PASS** | `test_temperature.py::test_tc15_missing_reading_detection` |
| **TC16** | Duplicate reading detection | Ingest identical `reading_id` twice | Idempotent upsert or duplicate rejection | Uniqueness preserved, zero duplicates | **PASS** | `test_temperature.py::test_tc16_duplicate_reading_detection` |

---

### Group C — Mandatory Negative Scenarios (TC17 – TC21)

| Test ID | Title | Input Parameters | Expected Result | Actual Result | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC17** | Unassigned logger | Reading submitted from logger without active assignment | Detected as `UNASSIGNED_LOGGER`, quarantined | Reading quarantined, flagged `UNASSIGNED_LOGGER` | **PASS** | `test_negative_scenarios.py::test_tc17_unassigned_logger` |
| **TC18** | Product threshold mismatch | Policy for `PROD-002` applied to `PROD-001` shipment | Evaluation blocked: `POLICY_MISMATCH` | Exception raised: `POLICY_MISMATCH` | **PASS** | `test_negative_scenarios.py::test_tc18_product_threshold_mismatch` |
| **TC19** | Missing data silently passed | 6 consecutive missing readings during transit | Rejects false `COMPLIANT`, returns `INCONCLUSIVE` | Returns `INCONCLUSIVE` with code `INSUFFICIENT_TELEMETRY` | **PASS** | `test_negative_scenarios.py::test_tc19_missing_data_silently_passed` |
| **TC20** | Custody gap not flagged | Missing intermediate custodian handoff | Detected as `CUSTODY_GAP`, flagged in report | Detected: `CUSTODY_GAP` at FRA transfer | **PASS** | `test_negative_scenarios.py::test_tc20_custody_gap_not_flagged` |
| **TC21** | Cross-shipment excursion duration | Overlapping excursions on `SHP-001` and `SHP-002` | Independent duration calculation per shipment | Calculated durations isolated (30m & 20m) | **PASS** | `test_negative_scenarios.py::test_tc21_cross_shipment_excursion_duration` |

---

### Group D — Compliance Decision Engine (TC22 – TC29)

| Test ID | Title | Input Parameters | Expected Result | Actual Result | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC22** | Compliant shipment | All readings within envelope, complete telemetry | Status: `COMPLIANT`, score = 100 | Result: `COMPLIANT`, score = 100.0 | **PASS** | `test_compliance.py::test_tc22_compliant_shipment` |
| **TC23** | Non-compliant shipment | Excursion duration 60 mins > allowed 30 mins | Status: `NON_COMPLIANT` | Result: `NON_COMPLIANT` | **PASS** | `test_compliance.py::test_tc23_non_compliant_shipment` |
| **TC24** | Inconclusive shipment | Telemetry dropouts exceed threshold | Status: `INCONCLUSIVE` | Result: `INCONCLUSIVE` | **PASS** | `test_compliance.py::test_tc24_inconclusive_shipment` |
| **TC25** | Under-review shipment | Shipment still in-transit or pending QA disposition | Status: `UNDER_REVIEW` | Result: `UNDER_REVIEW` | **PASS** | `test_compliance.py::test_tc25_under_review_shipment` |
| **TC26** | Compliance evidence traceability | Evaluate completed shipment | Report includes exact reading IDs & reason codes | Evidence array populated with traceable IDs | **PASS** | `test_compliance.py::test_tc26_compliance_evidence_traceability` |
| **TC27** | Historical policy version | Policy updated to `v2.0` after evaluation | Original report preserves `v1.0` | Report retains `policy_version: "v1.0"` | **PASS** | `test_compliance.py::test_tc27_historical_policy_version` |
| **TC28** | Calibration validation | Logger calibration expired 5 days prior to shipment | Flagged `CALIBRATION_EXPIRED`, compliance blocked | Blocked: `CALIBRATION_EXPIRED` | **PASS** | `test_compliance.py::test_tc28_calibration_validation` |
| **TC29** | Route dwell analysis | Airport dwell = 300 mins (threshold = 180 mins) | Flagged `EXCESSIVE_DWELL` on route stop | Flagged: `EXCESSIVE_DWELL` | **PASS** | `test_compliance.py::test_tc29_route_dwell_analysis` |

---

### Group E — Validation & Evaluation (TC30 – TC37)

| Test ID | Title | Input Parameters | Expected Result | Actual Result | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC30** | Primary-key uniqueness | Audit primary keys in all tables | 100% unique primary keys | Pass: Zero duplicate primary keys | **PASS** | `test_validation.py::test_tc30_primary_key_uniqueness` |
| **TC31** | Foreign-key integrity | Audit child-to-parent references | Zero orphan foreign keys | Pass: 100% integrity across tables | **PASS** | `test_validation.py::test_tc31_foreign_key_integrity` |
| **TC32** | Enum validation | Validate status strings against dictionaries | 100% valid enum values | Pass: All enums within domain | **PASS** | `test_validation.py::test_tc32_enum_validation` |
| **TC33** | Date ordering | Audit departure vs arrival, mfg vs expiry | Strictly chronological timestamps | Pass: All date sequences valid | **PASS** | `test_validation.py::test_tc33_date_ordering` |
| **TC34** | Derived value reconciliation | Compare compliance report derived vs raw counts | 0.00% discrepancy | Pass: Exact match between raw and derived | **PASS** | `test_validation.py::test_tc34_derived_value_reconciliation` |
| **TC35** | Ground-truth separation | Inspect operational detection services | Services do not read ground-truth files | Pass: Zero import of ground truth fixtures | **PASS** | `test_validation.py::test_tc35_ground_truth_separation` |
| **TC36** | Precision calculation | TP=48, FP=2, FN=0 | Precision = 48 / (48 + 2) = 0.96 | Computed Precision = 0.960 | **PASS** | `test_validation.py::test_tc36_precision_calculation` |
| **TC37** | Recall and F1 calculation | TP=48, FP=2, FN=2 | Recall = 0.96, F1 = 0.96 | Computed Recall = 0.960, F1 = 0.960 | **PASS** | `test_validation.py::test_tc37_recall_and_f1_calculation` |

---

### Group F — Export & Reproducibility (TC38 – TC43)

| Test ID | Title | Input Parameters | Expected Result | Actual Result | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC38** | CSV export | Export all core entities | Valid CSV files created in `data/exports/` | All CSV files generated with headers | **PASS** | `test_reproducibility.py::test_tc38_csv_export` |
| **TC39** | JSON export | Export all core entities | Valid JSON files created in `data/exports/` | Formatted JSON arrays generated | **PASS** | `test_reproducibility.py::test_tc39_json_export` |
| **TC40** | SQL seed export | Generate `seed_data.sql` | Executable SQL `INSERT` statements | SQL script generated with batch inserts | **PASS** | `test_reproducibility.py::test_tc40_sql_seed_export` |
| **TC41** | Fixed-seed reproducibility | Run A (Seed 20261022) vs Run B (Seed 20261022) | Matching SHA-256 dataset checksums | Checksums match identically: Match = True | **PASS** | `test_reproducibility.py::test_tc41_fixed_seed_reproducibility` |
| **TC42** | Different-seed variation | Run A (Seed 20261022) vs Run C (Seed 99999999) | Different SHA-256 dataset checksums | Checksums differ: Match = False | **PASS** | `test_reproducibility.py::test_tc42_different_seed_variation` |
| **TC43** | Manifest generation | Generate `manifest.json` | Manifest includes file hashes & record counts | Manifest generated with SHA-256 hashes | **PASS** | `test_reproducibility.py::test_tc43_manifest_generation` |

---

### Group G — Integration & Edge Cases (TC44 – TC50)

| Test ID | Title | Input Parameters | Expected Result | Actual Result | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC44** | Empty dataset handling | Query endpoints when zero shipments exist | Graceful return: empty list `[]`, meta total = 0 | Handled: `{ success: true, data: [] }` | **PASS** | `test_integration_edge_cases.py::test_tc44_empty_dataset` |
| **TC45** | Invalid API request | Malformed JSON payload to `/api/v1/shipments` | HTTP 400 Bad Request with error envelope | Returned HTTP 400 with `INVALID_PAYLOAD` | **PASS** | `test_integration_edge_cases.py::test_tc45_invalid_api_request` |
| **TC46** | Missing resource | GET `/api/v1/shipments/SHP-DOES-NOT-EXIST` | HTTP 404 Not Found | Returned HTTP 404 with `NOT_FOUND` | **PASS** | `test_integration_edge_cases.py::test_tc46_missing_resource` |
| **TC47** | Database failure handling | Simulate database disconnection | HTTP 500 with safe sanitized message | Returned HTTP 500, no leaked secrets | **PASS** | `test_integration_edge_cases.py::test_tc47_database_failure_handling` |
| **TC48** | Large dataset pagination | Request page 2 with limit 25 | Returns records 26 to 50 with pagination meta | Returns exactly 25 items with valid meta | **PASS** | `test_integration_edge_cases.py::test_tc48_large_dataset_pagination` |
| **TC49** | Concurrent generation protection | Trigger generator while another run is active | Returns HTTP 409 Conflict | Returned HTTP 409 `RUN_ALREADY_IN_PROGRESS` | **PASS** | `test_integration_edge_cases.py::test_tc49_concurrent_generation_protection` |
| **TC50** | Historical event preservation | Modify shipment status | Audit event recorded, original unchanged | Audit row created with before/after diff | **PASS** | `test_integration_edge_cases.py::test_tc50_historical_event_preservation` |
