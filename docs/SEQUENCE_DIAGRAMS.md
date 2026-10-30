# ColdChain IQ — Sequence Diagrams

## 1. Sequence Diagram 1: Telemetry Ingestion & Real-Time Auditing

Demonstrates the lifecycle of an incoming temperature reading, verifying logger assignment, applying calibration uncertainty offsets, and flagging unassigned sensors.

```mermaid
sequenceDiagram
    autonumber
    participant Sensor as IoT Data Logger
    participant Gateway as API Gateway (/api/v1/temperature)
    participant TempSvc as TemperatureService
    participant LoggerSvc as LoggerService
    participant SupaDB as Supabase Database

    Sensor->>Gateway: POST /readings (logger_id, shipment_id, temp, timestamp)
    Gateway->>TempSvc: ingest_reading(payload)
    TempSvc->>LoggerSvc: verify_logger_assignment(logger_id, shipment_id, timestamp)
    
    alt Logger is NOT assigned to shipment at timestamp
        LoggerSvc-->>TempSvc: Assignment Invalid (UNASSIGNED_LOGGER)
        TempSvc->>SupaDB: Insert reading (status='UNASSIGNED_LOGGER')
        TempSvc-->>Gateway: Flagged reading stored (Quarantined)
    else Logger has valid active assignment
        LoggerSvc-->>TempSvc: Assignment Valid + Return Calibration Offset
        TempSvc->>TempSvc: Calculate corrected_temperature = measured + offset
        TempSvc->>SupaDB: Insert reading (status='VALID')
        TempSvc->>TempSvc: audit_telemetry_gap(shipment_id, timestamp)
        TempSvc-->>Gateway: Reading accepted as trusted evidence
    end

    Gateway-->>Sensor: HTTP 201 Created (Ingestion receipt)
```

---

## 2. Sequence Diagram 2: 12-Step Compliance Determination

Illustrates the deterministic evaluation of a delivered shipment, executing all 12 validation steps and generating a traceable compliance certificate.

```mermaid
sequenceDiagram
    autonumber
    actor QA as QA / Operations Manager
    participant UI as React Frontend
    participant CompSvc as ComplianceService
    participant PolicySvc as ThresholdPolicyService
    participant TempSvc as TemperatureService
    participant CustodySvc as CustodyService
    participant SupaDB as Supabase Database

    QA->>UI: Click "Evaluate Shipment Compliance"
    UI->>CompSvc: POST /api/v1/compliance/analyze/{shipment_id}
    
    Note over CompSvc: Step 1-3: Validate Shipment, Product, Lot, Logger Assignment
    CompSvc->>PolicySvc: Step 4: Resolve Active Policy for Product
    
    alt Policy does not match shipment product
        PolicySvc-->>CompSvc: Error: POLICY_MISMATCH
        CompSvc-->>UI: HTTP 422 (Compliance blocked by Policy Mismatch)
    else Policy matched & active
        PolicySvc-->>CompSvc: Return Policy (min_temp, max_temp, allowed_duration)
        
        Note over CompSvc: Step 5-6: Audit Calibration & Evaluate Readings
        CompSvc->>TempSvc: Step 7-8: Detect Gaps & Calculate Excursion Durations
        TempSvc-->>CompSvc: Excursion Metrics (cumulative_mins, max_deviation)
        
        CompSvc->>CustodySvc: Step 10: Validate Chain of Custody
        CustodySvc-->>CompSvc: Custody Status (VERIFIED or CUSTODY_GAP)
        
        Note over CompSvc: Step 11: Compute Final Decision<br/>(COMPLIANT / NON_COMPLIANT / INCONCLUSIVE)
        
        CompSvc->>SupaDB: Step 12: Persist ComplianceReport & AuditEvent
        CompSvc-->>UI: Return Compliance Dossier & Reason Codes
        UI-->>QA: Render Interactive GxP Compliance Certificate
    end
```

---

## 3. Sequence Diagram 3: Cross-Shipment Excursion Isolation

Demonstrates how the engine isolates overlapping excursion readings between concurrent shipments, preventing cross-shipment contamination.

```mermaid
sequenceDiagram
    autonumber
    participant Ingestion as Ingestion Engine
    participant ExcrSvc as ExcursionService
    participant SupaDB as Supabase Database

    Note over Ingestion: Shipments SHP-001 and SHP-002 experience excursions at 14:00
    Ingestion->>SupaDB: Ingest out-of-spec readings for SHP-001
    Ingestion->>SupaDB: Ingest out-of-spec readings for SHP-002

    ExcrSvc->>ExcrSvc: calculate_excursions(shipment_id="SHP-001")
    ExcrSvc->>SupaDB: Query readings WHERE shipment_id = "SHP-001" ORDER BY recorded_at ASC
    SupaDB-->>ExcrSvc: Return strictly SHP-001 readings (3 readings = 30 mins)
    ExcrSvc->>ExcrSvc: Verify zero readings from SHP-002 included
    ExcrSvc->>SupaDB: Save ExcursionReport (SHP-001, duration=30 mins)

    ExcrSvc->>ExcrSvc: calculate_excursions(shipment_id="SHP-002")
    ExcrSvc->>SupaDB: Query readings WHERE shipment_id = "SHP-002" ORDER BY recorded_at ASC
    SupaDB-->>ExcrSvc: Return strictly SHP-002 readings (2 readings = 20 mins)
    ExcrSvc->>SupaDB: Save ExcursionReport (SHP-002, duration=20 mins)
```

---

## 4. Sequence Diagram 4: Offline Ground-Truth Evaluation

Demonstrates the strict air-gap between operational detection inputs and ground-truth evaluation metrics.

```mermaid
sequenceDiagram
    autonumber
    actor Analyst as Data Scientist / Analyst
    participant EvalSvc as EvaluationService
    participant SupaDB as Supabase Database (Operational Data)
    participant GTFiles as Quarantined Ground Truth (CSV/JSON)

    Analyst->>EvalSvc: POST /api/v1/evaluation/run
    
    Note over EvalSvc: Step 1: Query Operational Predictions
    EvalSvc->>SupaDB: Query operational compliance decisions & flagged anomalies
    SupaDB-->>EvalSvc: Return operational results (Predictions)
    
    Note over EvalSvc: Step 2: Read Quarantined Ground Truth
    EvalSvc->>GTFiles: Load ground_truth.json (Truth labels)
    GTFiles-->>EvalSvc: Return expected labels for injected scenarios
    
    Note over EvalSvc: Step 3: Compute Evaluation Metrics
    EvalSvc->>EvalSvc: Reconcile TP, FP, TN, FN
    EvalSvc->>EvalSvc: Calculate Precision = TP / (TP + FP)
    EvalSvc->>EvalSvc: Calculate Recall = TP / (TP + FN)
    EvalSvc->>EvalSvc: Calculate F1-Score = 2 * (P * R) / (P + R)
    
    EvalSvc-->>Analyst: Return Confusion Matrix & Scenario Breakdown
```
