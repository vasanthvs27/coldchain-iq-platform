# ColdChain IQ — Entity-Relationship Diagram

## 1. Complete Database Entity-Relationship Model

```mermaid
erDiagram
    PRODUCTS ||--o{ LOTS : "manufactures (1:N)"
    PRODUCTS ||--o{ THRESHOLD_POLICIES : "governed by (1:N)"
    PRODUCTS ||--o{ PACKAGING_PRODUCT_COMPATIBILITIES : "compatible with (N:M bridge)"
    PACKAGING ||--o{ PACKAGING_PRODUCT_COMPATIBILITIES : "supports (N:M bridge)"
    
    LOTS ||--o{ SHIPMENTS : "dispatched in (1:N)"
    PRODUCTS ||--o{ SHIPMENTS : "defines payload for (1:N)"
    PACKAGING ||--o{ SHIPMENTS : "protects (1:N)"
    
    SHIPMENTS ||--o{ SHIPMENT_LOGGER_ASSIGNMENTS : "assigned loggers (N:M bridge)"
    LOGGERS ||--o{ SHIPMENT_LOGGER_ASSIGNMENTS : "tracks shipments (N:M bridge)"
    
    SHIPMENTS ||--o{ TEMPERATURE_READINGS : "contains telemetry (1:N)"
    LOGGERS ||--o{ TEMPERATURE_READINGS : "records telemetry (1:N)"
    
    SHIPMENTS ||--o{ CUSTODY_EVENTS : "chain of custody (1:N)"
    SHIPMENTS ||--o{ ROUTE_STOPS : "route waypoints (1:N)"
    SHIPMENTS ||--o{ EXCURSION_REPORTS : "excursion violations (1:N)"
    SHIPMENTS ||--o{ COMPLIANCE_REPORTS : "compliance certifications (1:N)"
    
    ROLES ||--o{ USERS : "assigned to (1:N)"
    USERS ||--o{ AUDIT_EVENTS : "performed by (1:N)"

    PRODUCTS {
        varchar product_id PK
        varchar product_name
        varchar product_category
        numeric minimum_temperature
        numeric maximum_temperature
        integer allowed_excursion_duration
        varchar default_packaging_id FK
        integer shelf_life_days
        varchar status
        timestamptz effective_from
        timestamptz effective_until
    }

    LOTS {
        varchar lot_id PK
        varchar product_id FK
        varchar supplier_name
        date manufacturing_date
        date expiry_date
        numeric quantity
        varchar unit
        varchar lifecycle_status
    }

    SHIPMENTS {
        varchar shipment_id PK
        varchar lot_id FK
        varchar product_id FK
        varchar packaging_id FK
        varchar origin
        varchar destination
        varchar carrier_name
        timestamptz planned_departure
        timestamptz actual_departure
        timestamptz expected_arrival
        timestamptz actual_arrival
        varchar shipment_status
        varchar compliance_status
    }

    PACKAGING {
        varchar packaging_id PK
        varchar packaging_name
        varchar packaging_type
        numeric minimum_temperature
        numeric maximum_temperature
        integer validated_duration
        varchar insulation_type
        varchar status
    }

    LOGGERS {
        varchar logger_id PK
        varchar serial_number UK
        varchar model
        date calibration_date
        date calibration_expiry
        numeric accuracy_tolerance
        numeric measurement_uncertainty
        varchar battery_status
        varchar logger_status
    }

    SHIPMENT_LOGGER_ASSIGNMENTS {
        varchar assignment_id PK
        varchar shipment_id FK
        varchar logger_id FK
        timestamptz assigned_at
        timestamptz unassigned_at
        varchar status
    }

    TEMPERATURE_READINGS {
        varchar reading_id PK
        varchar logger_id FK
        varchar shipment_id FK
        timestamptz recorded_at
        numeric measured_temperature
        numeric corrected_temperature
        numeric calibration_uncertainty
        varchar reading_status
    }

    CUSTODY_EVENTS {
        varchar custody_event_id PK
        varchar shipment_id FK
        varchar previous_custodian
        varchar new_custodian
        varchar location
        timestamptz handoff_timestamp
        varchar event_type
        varchar acknowledgement_status
        varchar verification_status
    }

    ROUTE_STOPS {
        varchar route_stop_id PK
        varchar shipment_id FK
        integer stop_sequence
        varchar stop_name
        varchar stop_type
        timestamptz planned_arrival
        timestamptz actual_arrival
        timestamptz departure_time
        integer dwell_duration
        varchar status
    }

    THRESHOLD_POLICIES {
        varchar policy_id PK
        varchar product_id FK
        numeric minimum_temperature
        numeric maximum_temperature
        integer allowed_excursion_duration
        varchar policy_version
        varchar policy_status
        timestamptz effective_from
        timestamptz effective_until
    }

    EXCURSION_REPORTS {
        varchar excursion_id PK
        varchar shipment_id FK
        varchar product_id FK
        varchar lot_id FK
        varchar logger_id FK
        timestamptz start_timestamp
        timestamptz end_timestamp
        integer calculated_duration
        numeric minimum_observed_temperature
        numeric maximum_observed_temperature
        varchar severity
        varchar issue_type
        varchar investigation_status
        varchar compliance_decision
    }

    COMPLIANCE_REPORTS {
        varchar report_id PK
        varchar shipment_id FK
        varchar final_decision
        numeric compliance_score
        integer total_readings
        integer valid_readings
        integer missing_readings
        integer excursion_count
        timestamptz evaluated_at
    }

    AUDIT_EVENTS {
        varchar event_id PK
        varchar entity_type
        varchar entity_id
        varchar action
        varchar user_id FK
        varchar ip_address
        jsonb old_values
        jsonb new_values
        timestamptz created_at
    }
```

---

## 2. Cardinality & Relationship Breakdown

1. **Product to Lots (`1:N`)**: A pharmaceutical product formulation is produced in multiple batch manufacturing lots. Each lot references exactly one product.
2. **Product to Packaging (`N:M`)**: Products have validated compatibility with specific packaging types through the `packaging_product_compatibilities` bridge table.
3. **Lot to Shipments (`1:N`)**: A manufacturing lot is distributed across multiple shipments.
4. **Shipment to Loggers (`N:M` via `ShipmentLoggerAssignment`)**: A shipment may be monitored by primary and backup loggers; a logger is reused across multiple shipments over its lifecycle.
5. **Shipment to Temperature Readings (`1:N`)**: A shipment aggregates hundreds or thousands of timestamped sensor observations.
6. **Shipment to Custody Events (`1:N`)**: Tracks chronological handoffs between shippers, airlines, ground handlers, and clinical consignees.
7. **Shipment to Excursion Reports (`1:N`)**: Captures zero, one, or multiple out-of-specification thermal incidents.
8. **Shipment to Compliance Reports (`1:N`)**: Preserves all compliance evaluation audits, maintaining historical policy versions and decision histories.
