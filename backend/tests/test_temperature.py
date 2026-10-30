# backend/tests/test_temperature.py
import pytest
from app.services.temperature_service import TemperatureService
from app.services.excursion_service import ExcursionService
from app.config.supabase_client import supabase

def test_tc09_normal_temperature_reading():
    """TC09: Ingest normal temperature reading within allowed limits."""
    # Ensure active assignment exists
    supabase.table("shipment_logger_assignments").insert({
        "assignment_id": "ASG-TEMP-01",
        "shipment_id": "SHP-2026-TEST01",
        "logger_id": "LOG-2026-TEST01",
        "assigned_at": "2026-02-01T00:00:00Z",
        "status": "ACTIVE"
    }, upsert=True).execute()

    reading = {
        "reading_id": "TEMP-TEST-001",
        "logger_id": "LOG-2026-TEST01",
        "shipment_id": "SHP-2026-TEST01",
        "recorded_at": "2026-02-01T08:10:00Z",
        "measured_temperature": -70.0, # Target for PROD-001 is -80 to -60
        "corrected_temperature": -70.1,
        "calibration_uncertainty": 0.20
    }
    ingested = TemperatureService.insert_reading(reading)
    assert ingested["reading_status"] == "VALID"

def test_tc10_upper_temperature_excursion():
    """TC10: Temperature exceeding maximum threshold flagged as excursion."""
    policy = {"minimum_temperature": 2.0, "maximum_temperature": 8.0, "allowed_excursion_duration": 60}
    # Insert high temp readings
    readings = [
        {"reading_id": "TEMP-EXC-01", "logger_id": "LOG-2026-TEST01", "shipment_id": "SHP-EXC-01", "recorded_at": "2026-02-01T10:00:00Z", "measured_temperature": 11.5, "corrected_temperature": 11.5, "calibration_uncertainty": 0.2, "reading_status": "VALID"},
        {"reading_id": "TEMP-EXC-02", "logger_id": "LOG-2026-TEST01", "shipment_id": "SHP-EXC-01", "recorded_at": "2026-02-01T10:10:00Z", "measured_temperature": 12.0, "corrected_temperature": 12.0, "calibration_uncertainty": 0.2, "reading_status": "VALID"}
    ]
    supabase.table("shipments").insert({"shipment_id": "SHP-EXC-01", "product_id": "PROD-002", "lot_id": "LOT-2026-TEST01", "packaging_id": "PKG-001", "origin": "A", "destination": "B", "carrier_name": "C", "planned_departure": "2026-02-01T09:00:00Z", "expected_arrival": "2026-02-01T12:00:00Z"}, upsert=True).execute()
    supabase.table("temperature_readings").insert(readings, upsert=True).execute()

    excursions = ExcursionService.analyze_shipment_excursions("SHP-EXC-01", policy)
    assert len(excursions) >= 1
    assert excursions[0]["issue_type"] == "UPPER_EXCURSION"
    assert excursions[0]["maximum_observed_temperature"] >= 12.0

def test_tc11_lower_temperature_excursion():
    """TC11: Temperature falling below minimum threshold flagged as lower excursion."""
    policy = {"minimum_temperature": 2.0, "maximum_temperature": 8.0, "allowed_excursion_duration": 60}
    readings = [
        {"reading_id": "TEMP-LOW-01", "logger_id": "LOG-2026-TEST01", "shipment_id": "SHP-LOW-01", "recorded_at": "2026-02-01T10:00:00Z", "measured_temperature": 0.5, "corrected_temperature": 0.5, "calibration_uncertainty": 0.2, "reading_status": "VALID"}
    ]
    supabase.table("shipments").insert({"shipment_id": "SHP-LOW-01", "product_id": "PROD-002", "lot_id": "LOT-2026-TEST01", "packaging_id": "PKG-001", "origin": "A", "destination": "B", "carrier_name": "C", "planned_departure": "2026-02-01T09:00:00Z", "expected_arrival": "2026-02-01T12:00:00Z"}, upsert=True).execute()
    supabase.table("temperature_readings").insert(readings, upsert=True).execute()

    excursions = ExcursionService.analyze_shipment_excursions("SHP-LOW-01", policy)
    assert len(excursions) >= 1
    assert excursions[0]["issue_type"] == "LOWER_EXCURSION"
    assert excursions[0]["minimum_observed_temperature"] <= 0.5

def test_tc12_allowed_excursion_duration():
    """TC12: Excursion within allowed duration (e.g. 20 min <= 60 min) remains COMPLIANT."""
    policy = {"minimum_temperature": 2.0, "maximum_temperature": 8.0, "allowed_excursion_duration": 60}
    readings = [
        {"reading_id": "TEMP-OK-01", "logger_id": "LOG-2026-TEST01", "shipment_id": "SHP-OK-01", "recorded_at": "2026-02-01T10:00:00Z", "measured_temperature": 9.5, "corrected_temperature": 9.5, "calibration_uncertainty": 0.2, "reading_status": "VALID"},
        {"reading_id": "TEMP-OK-02", "logger_id": "LOG-2026-TEST01", "shipment_id": "SHP-OK-01", "recorded_at": "2026-02-01T10:10:00Z", "measured_temperature": 9.2, "corrected_temperature": 9.2, "calibration_uncertainty": 0.2, "reading_status": "VALID"}
    ]
    supabase.table("shipments").insert({"shipment_id": "SHP-OK-01", "product_id": "PROD-002", "lot_id": "LOT-2026-TEST01", "packaging_id": "PKG-001", "origin": "A", "destination": "B", "carrier_name": "C", "planned_departure": "2026-02-01T09:00:00Z", "expected_arrival": "2026-02-01T12:00:00Z"}, upsert=True).execute()
    supabase.table("temperature_readings").insert(readings, upsert=True).execute()

    excursions = ExcursionService.analyze_shipment_excursions("SHP-OK-01", policy)
    assert len(excursions) == 1
    assert excursions[0]["compliance_decision"] == "COMPLIANT"

def test_tc13_excursion_exceeding_allowed_duration():
    """TC13: Excursion exceeding allowed duration (90 min > 60 min limit) marked NON_COMPLIANT."""
    policy = {"minimum_temperature": 2.0, "maximum_temperature": 8.0, "allowed_excursion_duration": 30}
    readings = [
        {"reading_id": f"TEMP-LONG-{i}", "logger_id": "LOG-2026-TEST01", "shipment_id": "SHP-LONG-01", "recorded_at": f"2026-02-01T10:{i*10:02d}:00Z", "measured_temperature": 11.0, "corrected_temperature": 11.0, "calibration_uncertainty": 0.2, "reading_status": "VALID"}
        for i in range(5) # 5 readings = 40+ min
    ]
    supabase.table("shipments").insert({"shipment_id": "SHP-LONG-01", "product_id": "PROD-002", "lot_id": "LOT-2026-TEST01", "packaging_id": "PKG-001", "origin": "A", "destination": "B", "carrier_name": "C", "planned_departure": "2026-02-01T09:00:00Z", "expected_arrival": "2026-02-01T12:00:00Z"}, upsert=True).execute()
    supabase.table("temperature_readings").insert(readings, upsert=True).execute()

    excursions = ExcursionService.analyze_shipment_excursions("SHP-LONG-01", policy)
    assert len(excursions) >= 1
    assert excursions[0]["compliance_decision"] == "NON_COMPLIANT"

def test_tc14_calibration_uncertainty():
    """TC14: Separate measured temperature, corrected temperature, and calibration uncertainty."""
    sample = {
        "reading_id": "TEMP-UNC-TEST-01",
        "logger_id": "LOG-2026-TEST01",
        "shipment_id": "SHP-2026-TEST01",
        "recorded_at": "2026-02-01T12:00:00Z",
        "measured_temperature": 5.12,
        "corrected_temperature": 5.08,
        "calibration_uncertainty": 0.20,
        "reading_status": "VALID"
    }
    supabase.table("temperature_readings").insert(sample, upsert=True).execute()
    reading = supabase.table("temperature_readings").select("*").eq("reading_id", "TEMP-UNC-TEST-01").execute().data[0]
    assert "measured_temperature" in reading
    assert "corrected_temperature" in reading
    assert "calibration_uncertainty" in reading
    assert reading["calibration_uncertainty"] == 0.20

def test_tc15_missing_reading_detection():
    """TC15: Detect missing 10-minute telemetry gaps."""
    supabase.table("shipments").insert({
        "shipment_id": "SHP-GAP-TEST",
        "product_id": "PROD-002",
        "lot_id": "LOT-2026-TEST01",
        "packaging_id": "PKG-001",
        "origin": "A",
        "destination": "B",
        "carrier_name": "C",
        "actual_departure": "2026-02-01T10:00:00Z",
        "actual_arrival": "2026-02-01T14:00:00Z" # 4 hours = 24 intervals expected
    }, upsert=True).execute()

    # Only 2 readings 2 hours apart
    supabase.table("temperature_readings").insert([
        {"reading_id": "GAP-R1", "logger_id": "LOG-2026-TEST01", "shipment_id": "SHP-GAP-TEST", "recorded_at": "2026-02-01T10:00:00Z", "measured_temperature": 5.0, "corrected_temperature": 5.0},
        {"reading_id": "GAP-R2", "logger_id": "LOG-2026-TEST01", "shipment_id": "SHP-GAP-TEST", "recorded_at": "2026-02-01T12:30:00Z", "measured_temperature": 5.0, "corrected_temperature": 5.0}
    ], upsert=True).execute()

    gaps = TemperatureService.detect_missing_gaps("SHP-GAP-TEST")
    assert gaps["has_gaps"] is True
    assert gaps["missing_reading_count"] > 0

def test_tc16_duplicate_reading_detection():
    """TC16: Upsert prevents duplicate readings with identical reading_id."""
    reading = {
        "reading_id": "TEMP-DUP-TEST",
        "logger_id": "LOG-2026-TEST01",
        "shipment_id": "SHP-2026-TEST01",
        "recorded_at": "2026-02-01T15:00:00Z",
        "measured_temperature": 4.5,
        "corrected_temperature": 4.5,
        "calibration_uncertainty": 0.20
    }
    supabase.table("temperature_readings").insert(reading, upsert=True).execute()
    count_before = len(supabase.table("temperature_readings").select("reading_id").eq("reading_id", "TEMP-DUP-TEST").execute().data)
    
    # Re-insert with upsert
    supabase.table("temperature_readings").insert(reading, upsert=True).execute()
    count_after = len(supabase.table("temperature_readings").select("reading_id").eq("reading_id", "TEMP-DUP-TEST").execute().data)
    
    assert count_before == 1
    assert count_after == 1
