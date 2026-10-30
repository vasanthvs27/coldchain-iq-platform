# backend/tests/test_compliance.py
import pytest
from datetime import datetime, timezone, timedelta
from app.services.compliance_service import ComplianceService
from app.services.logger_service import LoggerService
from app.config.supabase_client import supabase

def test_tc22_compliant_shipment():
    """TC22: Valid readings within range produce COMPLIANT status."""
    shipment_id = "SHP-COMPLIANT-OK"
    base_t = datetime(2026, 2, 1, 8, 0, 0, tzinfo=timezone.utc)
    arr_t = base_t + timedelta(hours=2)

    supabase.table("shipments").insert({
        "shipment_id": shipment_id,
        "product_id": "PROD-002",
        "lot_id": "LOT-2026-TEST01",
        "packaging_id": "PKG-001",
        "origin": "Origin Hub",
        "destination": "Dest Hub",
        "carrier_name": "Reliable Carrier",
        "actual_departure": base_t.isoformat(),
        "actual_arrival": arr_t.isoformat()
    }, upsert=True).execute()

    supabase.table("shipment_logger_assignments").insert({
        "assignment_id": f"ASG-{shipment_id}",
        "shipment_id": shipment_id,
        "logger_id": "LOG-2026-TEST01",
        "assigned_at": (base_t - timedelta(hours=1)).isoformat(),
        "status": "ACTIVE"
    }, upsert=True).execute()

    # Generate normal readings every 10 min up to arrival
    readings = []
    for i in range(13):
        t = base_t + timedelta(minutes=i*10)
        readings.append({
            "reading_id": f"R-{shipment_id}-{i}",
            "logger_id": "LOG-2026-TEST01",
            "shipment_id": shipment_id,
            "recorded_at": t.isoformat(),
            "measured_temperature": 5.0,
            "corrected_temperature": 5.0,
            "calibration_uncertainty": 0.20,
            "reading_status": "VALID"
        })
    supabase.table("temperature_readings").insert(readings, upsert=True).execute()

    supabase.table("custody_events").insert([
        {"custody_event_id": f"CUST-{shipment_id}-1", "shipment_id": shipment_id, "previous_custodian": "A", "new_custodian": "B", "location": "Hub", "handoff_timestamp": base_t.isoformat()}
    ], upsert=True).execute()

    report = ComplianceService.analyze_shipment_compliance(shipment_id)
    assert report["compliance_status"] == "COMPLIANT"
    assert report["compliance_score"] >= 90.0

def test_tc23_non_compliant_shipment():
    """TC23: Excursion exceeding limit results in NON_COMPLIANT status."""
    shipment_id = "SHP-NONCOMPLIANT-EXC"
    base_t = datetime(2026, 2, 1, 8, 0, 0, tzinfo=timezone.utc)
    arr_t = base_t + timedelta(hours=3)

    supabase.table("shipments").insert({
        "shipment_id": shipment_id,
        "product_id": "PROD-002",
        "lot_id": "LOT-2026-TEST01",
        "packaging_id": "PKG-001",
        "origin": "A",
        "destination": "B",
        "carrier_name": "C",
        "actual_departure": base_t.isoformat(),
        "actual_arrival": arr_t.isoformat()
    }, upsert=True).execute()

    supabase.table("shipment_logger_assignments").insert({
        "assignment_id": f"ASG-{shipment_id}",
        "shipment_id": shipment_id,
        "logger_id": "LOG-2026-TEST01",
        "assigned_at": (base_t - timedelta(hours=1)).isoformat(),
        "status": "ACTIVE"
    }, upsert=True).execute()

    # Sustained high temp excursion: 8 readings at 10-minute intervals (70 minutes > 60 min limit)
    readings = []
    for i in range(8):
        t = base_t + timedelta(minutes=i*10)
        readings.append({
            "reading_id": f"R-HOT-{shipment_id}-{i}",
            "logger_id": "LOG-2026-TEST01",
            "shipment_id": shipment_id,
            "recorded_at": t.isoformat(),
            "measured_temperature": 15.0,
            "corrected_temperature": 15.0,
            "reading_status": "VALID"
        })
    supabase.table("temperature_readings").insert(readings, upsert=True).execute()

    report = ComplianceService.analyze_shipment_compliance(shipment_id)
    assert report["compliance_status"] == "NON_COMPLIANT"
    assert "TEMPERATURE_EXCURSION_EXCEEDED" in report["reason_codes"]

def test_tc24_inconclusive_shipment():
    """TC24: Missing critical telemetry without confirmed excursion results in INCONCLUSIVE."""
    shipment_id = "SHP-INCONCLUSIVE-TEST"
    base_t = datetime(2026, 2, 1, 8, 0, 0, tzinfo=timezone.utc)
    arr_t = base_t + timedelta(hours=10)

    supabase.table("shipments").insert({
        "shipment_id": shipment_id,
        "product_id": "PROD-002",
        "lot_id": "LOT-2026-TEST01",
        "packaging_id": "PKG-001",
        "origin": "A",
        "destination": "B",
        "carrier_name": "C",
        "actual_departure": base_t.isoformat(),
        "actual_arrival": arr_t.isoformat()
    }, upsert=True).execute()

    supabase.table("shipment_logger_assignments").insert({
        "assignment_id": f"ASG-{shipment_id}",
        "shipment_id": shipment_id,
        "logger_id": "LOG-2026-TEST01",
        "assigned_at": (base_t - timedelta(hours=1)).isoformat(),
        "status": "ACTIVE"
    }, upsert=True).execute()

    # Only 1 reading out of 60 expected readings (< 10% coverage)
    supabase.table("temperature_readings").insert([
        {"reading_id": f"R-SPARSE-{shipment_id}", "logger_id": "LOG-2026-TEST01", "shipment_id": shipment_id, "recorded_at": base_t.isoformat(), "measured_temperature": 5.0, "corrected_temperature": 5.0, "reading_status": "VALID"}
    ], upsert=True).execute()

    report = ComplianceService.analyze_shipment_compliance(shipment_id)
    assert report["compliance_status"] == "INCONCLUSIVE"
    assert "MISSING_DATA" in report["reason_codes"]

def test_tc25_under_review_shipment():
    """TC25: Broken custody chain without excursion results in UNDER_REVIEW."""
    shipment_id = "SHP-UNDER-REVIEW-CUST"
    base_t = datetime(2026, 2, 1, 8, 0, 0, tzinfo=timezone.utc)
    arr_t = base_t + timedelta(hours=1)

    supabase.table("shipments").insert({
        "shipment_id": shipment_id,
        "product_id": "PROD-002",
        "lot_id": "LOT-2026-TEST01",
        "packaging_id": "PKG-001",
        "origin": "A",
        "destination": "B",
        "carrier_name": "C",
        "actual_departure": base_t.isoformat(),
        "actual_arrival": arr_t.isoformat()
    }, upsert=True).execute()

    supabase.table("shipment_logger_assignments").insert({
        "assignment_id": f"ASG-{shipment_id}",
        "shipment_id": shipment_id,
        "logger_id": "LOG-2026-TEST01",
        "assigned_at": (base_t - timedelta(hours=1)).isoformat(),
        "status": "ACTIVE"
    }, upsert=True).execute()

    readings = []
    for i in range(6):
        t = base_t + timedelta(minutes=i*10)
        readings.append({
            "reading_id": f"R-OK-{shipment_id}-{i}",
            "logger_id": "LOG-2026-TEST01",
            "shipment_id": shipment_id,
            "recorded_at": t.isoformat(),
            "measured_temperature": 5.0,
            "corrected_temperature": 5.0,
            "reading_status": "VALID"
        })
    supabase.table("temperature_readings").insert(readings, upsert=True).execute()

    # Inject broken custody chain
    supabase.table("custody_events").insert([
        {"custody_event_id": f"CUST-UR-1", "shipment_id": shipment_id, "previous_custodian": "Carrier X", "new_custodian": "Carrier Y", "location": "Hub 1", "handoff_timestamp": base_t.isoformat()},
        {"custody_event_id": f"CUST-UR-2", "shipment_id": shipment_id, "previous_custodian": "Rogue Z", "new_custodian": "Dest Dock", "location": "Hub 2", "handoff_timestamp": (base_t + timedelta(minutes=30)).isoformat()}
    ], upsert=True).execute()

    report = ComplianceService.analyze_shipment_compliance(shipment_id)
    assert report["compliance_status"] == "UNDER_REVIEW"
    assert "CUSTODY_GAP" in report["reason_codes"]

def test_tc26_compliance_evidence_traceability():
    """TC26: Compliance decision contains traceable reason codes and evidence references."""
    report = ComplianceService.get_report_for_shipment("SHP-NONCOMPLIANT-EXC")
    assert report is not None
    assert isinstance(report["reason_codes"], list)
    assert isinstance(report["evidence_references"], list)
    assert len(report["evidence_references"]) > 0

def test_tc27_historical_policy_version():
    """TC27: Compliance report preserves policy version used during evaluation."""
    report = ComplianceService.get_report_for_shipment("SHP-COMPLIANT-OK")
    assert report is not None
    assert "policy_version" in report
    assert report["policy_version"].startswith("v")

def test_tc28_calibration_validation():
    """TC28: Logger calibration expiry is evaluated and reported."""
    logger_id = "LOG-EXPIRED-TEST"
    supabase.table("loggers").insert({
        "logger_id": logger_id,
        "serial_number": "SN-EXP-001",
        "model": "SenseAware",
        "calibration_date": "2024-01-01T00:00:00Z",
        "calibration_expiry": "2025-01-01T00:00:00Z"
    }, upsert=True).execute()

    check = LoggerService.validate_calibration(logger_id)
    assert check["valid"] is False
    assert check["status"] == "EXPIRED"

def test_tc29_route_dwell_analysis():
    """TC29: Route dwell exceeding 240 minutes flagged as EXCESSIVE_ROUTE_DWELL."""
    shipment_id = "SHP-DWELL-TEST"
    base_t = datetime(2026, 2, 1, 8, 0, 0, tzinfo=timezone.utc)
    arr_t = base_t + timedelta(hours=7)

    supabase.table("shipments").insert({
        "shipment_id": shipment_id,
        "product_id": "PROD-002",
        "lot_id": "LOT-2026-TEST01",
        "packaging_id": "PKG-001",
        "origin": "A",
        "destination": "B",
        "carrier_name": "C",
        "actual_departure": base_t.isoformat(),
        "actual_arrival": arr_t.isoformat()
    }, upsert=True).execute()

    supabase.table("shipment_logger_assignments").insert({
        "assignment_id": f"ASG-{shipment_id}",
        "shipment_id": shipment_id,
        "logger_id": "LOG-2026-TEST01",
        "assigned_at": (base_t - timedelta(hours=1)).isoformat(),
        "status": "ACTIVE"
    }, upsert=True).execute()

    readings = []
    for i in range(7):
        t = base_t + timedelta(hours=i)
        readings.append({
            "reading_id": f"R-DW-{shipment_id}-{i}",
            "logger_id": "LOG-2026-TEST01",
            "shipment_id": shipment_id,
            "recorded_at": t.isoformat(),
            "measured_temperature": 5.0,
            "corrected_temperature": 5.0,
            "reading_status": "VALID"
        })
    supabase.table("temperature_readings").insert(readings, upsert=True).execute()

    # Route stop with 300 minutes dwell (5 hours)
    supabase.table("route_stops").insert({
        "route_stop_id": f"STOP-{shipment_id}-1",
        "shipment_id": shipment_id,
        "stop_sequence": 1,
        "stop_name": "Transit Hub Chicago",
        "stop_type": "HUB",
        "planned_arrival": (base_t + timedelta(hours=1)).isoformat(),
        "actual_arrival": (base_t + timedelta(hours=1)).isoformat(),
        "departure_time": (base_t + timedelta(hours=6)).isoformat(),
        "dwell_duration": 300,
        "status": "COMPLETED"
    }, upsert=True).execute()

    report = ComplianceService.analyze_shipment_compliance(shipment_id)
    assert "EXCESSIVE_ROUTE_DWELL" in report["reason_codes"]
