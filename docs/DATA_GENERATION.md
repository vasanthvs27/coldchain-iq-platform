# Synthetic Data Generation Engine

## 1. Engine Architecture & Design Goals

The ColdChain IQ Synthetic Data Generation Engine is a high-throughput, deterministic data pipeline built in pure Python. It is designed to generate realistic cold-chain telemetry and operational events for enterprise performance testing, regulatory validation, and machine learning ground-truth benchmarks.

- **Primary Random Seed**: `20261022` (Fixed for reproducibility).
- **Service Implementation**: `backend/app/services/generator_service.py`
- **CLI Utility**: `backend/scripts/generate_dataset.py`
- **Database Engine**: Writes directly to Supabase via the official Supabase Python client.

---

## 2. Dataset Modes & Volume Specifications

| Specification | Starter Mode (Development & CI) | Full Mode (72-Hour Assessment Baseline) |
| :--- | :--- | :--- |
| **Shipments** | 50 shipments | **5,000 shipments** |
| **Physical Loggers** | 20 loggers | **1,000 loggers** |
| **Telemetry Cadence** | 10 minutes | **10 minutes** |
| **Total Telemetry Readings** | ~3,600 readings | **~360,000 to 500,000+ readings** |
| **Route Stops** | ~150 waypoints | ~15,000 waypoints |
| **Custody Events** | ~100 handoffs | ~10,000 handoffs |
| **Excursions Injected** | ~8 excursions | ~750 excursions |
| **Negative Scenarios** | 5 controlled injections | 50+ controlled injections |
| **Target Generation Time** | < 2 seconds | < 45 seconds (bulk-batched) |

---

## 3. Strict Parent-First Generation Sequence

To maintain referential integrity without orphan records, entities are created in a strict topological order:

```text
Phase 1: Master Reference Data
  1. Products (e.g. Comirnaty mRNA, Humalog Insulin, Herceptin Monoclonal)
  2. Thermal Packaging Profiles (VIP Shippers, Active Dry Ice, Refrigerated Vans)
  3. Packaging-Product Compatibility Bridges
  4. Manufacturing Lots (Batch release dates, units, expiry)
  5. NIST-Calibrated Loggers (Serial numbers, calibration certificates)
  6. Threshold Policies (Versioned temperature bounds & allowed excursion minutes)

Phase 2: Operational Journeys & Assignments
  7. Shipments (Origin, destination, planned/actual departure and arrival)
  8. Shipment Logger Assignments (Time-bounded logger bindings)
  9. Route Waypoints & Airport Dwell Stops

Phase 3: Sensor Telemetry & Event Ingestion
 10. Timestamped Temperature Readings (10-minute cadence per logger assignment)
 11. Chain of Custody Transfer Records (Handoff events, locations, signatures)

Phase 4: Compliance & Exception Artifacts
 12. Excursion Reports (Calculated duration, severity, min/max observed)
 13. Official GxP Compliance Reports (12-step certification, reason codes)
 14. Quarantined Ground Truth Labels (Isolated CSV & JSON fixtures)
```

---

## 4. Realistic Synthetic Variations

The generator simulates real-world physical and logistic dynamics using parameterized statistical distributions:

1. **Thermal Stability Simulation**:
   - Baseline temperature is generated via Ornstein-Uhlenbeck mean-reverting stochastic processes:
     $$T_{t+1} = T_t + \theta (\mu - T_t) \Delta t + \sigma \sqrt{\Delta t} \cdot \mathcal{N}(0, 1)$$
   - Simulates ambient thermal diffusion through vacuum insulated panels (VIP).
2. **Upper-Bound Excursions (Heat Ingress)**:
   - Simulates airport tarmac exposure (+28°C to +38°C ambient) during summer transfers or refrigeration compressor failure.
3. **Lower-Bound Excursions (Freeze Damage)**:
   - Simulates direct dry ice contact or thermostat failure dropping temperature below freezing (-4°C to -15°C for refrigerated products).
4. **Telemetry Blackouts & Communication Dropouts**:
   - Injects intermittent missing readings simulating RF attenuation inside aircraft cargo holds or customs bonded vaults.
5. **Route Dwell Events**:
   - Simulates customs clearance bottlenecks with dwell times exceeding 4 hours.

---

## 5. Controlled Anomaly Injection & Ground Truth Isolation

The generator injects the 5 mandatory negative scenarios at known locations while maintaining **strict data isolation**:

1. **`UNASSIGNED_LOGGER`**: A reading from an active logger is recorded with a shipment ID that has no corresponding logger assignment record.
2. **`POLICY_MISMATCH`**: A shipment for a +2°C to +8°C vaccine is assigned a -70°C cryogenic policy.
3. **`MISSING_DATA`**: Readings are deleted for a 70-minute window during active transit.
4. **`CUSTODY_GAP`**: An intermediate custody transfer record is omitted between airline release and hospital receipt.
5. **`CROSS_SHIPMENT_DURATION`**: Two overlapping excursion fixtures are generated to verify that duration algorithms filter strictly on `shipment_id`.

### Ground Truth Quarantine
Ground-truth annotations are stored exclusively in:
- `data/ground_truth/ground_truth.csv`
- `data/ground_truth/ground_truth.json`

The operational API and compliance calculation services do not read or import these files. They are utilized solely by the offline `EvaluationService`.

---

## 6. Execution Instructions

### Run via Backend CLI
```powershell
# Navigate to backend
cd backend

# Generate in Starter Mode (50 shipments)
..\venv\Scripts\python scripts/generate_dataset.py --mode starter --seed 20261022

# Generate in Full Mode (5,000 shipments)
..\venv\Scripts\python scripts/generate_dataset.py --mode full --seed 20261022
```

### Run via REST API
```http
POST /api/v1/generator/run
Content-Type: application/json

{
  "mode": "starter",
  "seed": 20261022,
  "shipment_count": 50,
  "logger_count": 20,
  "reading_interval": 10
}
```

### Run via React Web Interface
Navigate to **Synthetic Generator** (`/generator`) in the web dashboard, select **Starter Mode** or **Full 5,000 Baseline**, verify the fixed seed `20261022`, and click **Launch Generation Run**.
