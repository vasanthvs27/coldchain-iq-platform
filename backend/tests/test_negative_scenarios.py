# backend/tests/test_negative_scenarios.py
import pytest
from app.services.temperature_service import TemperatureService
from app.services.compliance_service import ComplianceService
from app.services.custody_service import CustodyService
from app.services.excursion_service import ExcursionService
from app.config.supabase_client import supabase

def test_tc17_unassigned_logger():
    """
    TC17 / Negative Scenario 1: Unassigned Logger Detection (UNASSIGNED_LOGGER)
    A reading with an unassigned logger must be flagged, excluded from trusted evidence,
    and must not be silently accepted.
    """
    reading_payload = {
        "reading_id": "TEMP-ROUGE-001",
        "logger_id": "LOG-ROGUE-9999", # not assigned to shipment
        "shipment_id": "SHP-2026-TEST01",
        "recorded_at": "2026-02-01T11:00:00Z",
        "measured_temperature": 5.0,
        "corrected_temperature": 5.0
    }
    ingested = TemperatureService.insert_reading(reading_payload)
    assert ingested["reading_status"] == "UNASSIGNED_LOGGER"

    # In compliance evaluation, it must be flagged
    report = ComplianceService.analyze_shipment_compliance("SHP-2026-TEST01")
    assert "UNASSIGNED_LOGGER" in report["reason_codes"]
    assert report["compliance_status"] in ("UNDER_REVIEW", "INCONCLUSIVE", "NON_COMPLIANT")

def test_tc18_product_threshold_mismatch():
    """
    TC18 / Negative Scenario 2: Product Threshold Mismatch (POLICY_MISMATCH)
    Applying a policy from a different product must block standard compliance,
    display both policies, and flag POLICY_MISMATCH.
    """
    # Shipment is for PROD-001 (mRNA vaccine -80 to -60C)
    # Apply policy POL-2026-000002 which belongs to PROD-002 (Insulin 2-8C)
    report = ComplianceService.analyze_shipment_compliance("SHP-2026-TEST01", applied_policy_id="POL-2026-000002")
    assert "POLICY_MISMATCH" in report["reason_codes"]
    assert report["compliance_status"] == "UNDER_REVIEW"

def test_tc19_missing_data_silently_passed():
    """
    TC19 / Negative Scenario 3: Missing Data Silently Passed (MISSING_DATA)
    Missing required telemetry evidence must NEVER automatically result in COMPLIANT.
    Must return INCONCLUSIVE or NON_COMPLIANT.
    """
    supabase.table("shipments").insert({
        "shipment_id": "SHP-EMPTY-TELEMETRY",
        "product_id": "PROD-002",
        "lot_id": "LOT-2026-TEST01",
        "packaging_id": "PKG-001",
        "origin": "Boston",
        "destination": "London",
        "carrier_name": "Carrier",
        "actual_departure": "2026-02-01T10:00:00Z",
        "actual_arrival": "2026-02-01T20:00:00Z"
    }, upsert=True).execute()

    report = ComplianceService.analyze_shipment_compliance("SHP-EMPTY-TELEMETRY")
    assert "MISSING_DATA" in report["reason_codes"]
    assert report["compliance_status"] != "COMPLIANT"
    assert report["compliance_status"] in ("INCONCLUSIVE", "UNDER_REVIEW")

def test_tc20_custody_gap_not_flagged():
    """
    TC20 / Negative Scenario 4: Custody Gap Detection (CUSTODY_GAP)
    An incomplete custody chain or mismatched handoff must be flagged with details
    of previous and next custodians.
    """
    shipment_id = "SHP-CUST-BROKEN"
    supabase.table("shipments").insert({
        "shipment_id": shipment_id,
        "product_id": "PROD-002",
        "lot_id": "LOT-2026-TEST01",
        "packaging_id": "PKG-001",
        "origin": "Boston",
        "destination": "Frankfurt",
        "carrier_name": "Carrier"
    }, upsert=True).execute()

    supabase.table("custody_events").insert([
        {
            "custody_event_id": "CUST-GAP-01",
            "shipment_id": shipment_id,
            "previous_custodian": "Boston Hub",
            "new_custodian": "AirCargo North",
            "location": "Boston",
            "handoff_timestamp": "2026-02-01T08:00:00Z"
        },
        {
            "custody_event_id": "CUST-GAP-02",
            "shipment_id": shipment_id,
            "previous_custodian": "Unknown Third Party", # Discontinuity! Expected AirCargo North
            "new_custodian": "Frankfurt Receiving",
            "location": "Frankfurt",
            "handoff_timestamp": "2026-02-01T18:00:00Z"
        }
    ], upsert=True).execute()

    gap_analysis = CustodyService.detect_custody_gaps(shipment_id)
    assert gap_analysis["has_gaps"] is True
    assert any(g.get("issue_code") == "CUSTODY_GAP" for g in gap_analysis["gaps"])

def test_tc21_cross_shipment_excursion_duration():
    """
    TC21 / Negative Scenario 5: Cross-Shipment Duration Isolation (CROSS_SHIPMENT_DURATION)
    Excursions from two different shipments must NEVER be combined into a single event.
    Must detect cross contamination and isolate them independently.
    """
    overlapping_fixtures = [
        {"shipment_id": "SHP-A", "excursion_id": "EXCR-A-01", "calculated_duration": 40},
        {"shipment_id": "SHP-B", "excursion_id": "EXCR-B-01", "calculated_duration": 40}
    ]
    check = ExcursionService.detect_cross_shipment_anomaly(overlapping_fixtures)
    assert check["detected"] is True
    assert check["error_code"] == "CROSS_SHIPMENT_DURATION"
    assert "isolated_excursions" in check
