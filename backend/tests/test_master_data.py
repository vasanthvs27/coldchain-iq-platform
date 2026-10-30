# backend/tests/test_master_data.py
import pytest
from app.services.product_service import ProductService
from app.services.logger_service import LoggerService
from app.config.supabase_client import supabase

def test_tc01_product_creation():
    """TC01: Product creation with valid temperature boundaries."""
    prod = {
        "product_id": "PROD-TEST-001",
        "product_name": "Test Cryo Antigen",
        "product_category": "VACCINE",
        "minimum_temperature": 2.0,
        "maximum_temperature": 8.0,
        "allowed_excursion_duration": 45
    }
    created = ProductService.create(prod)
    assert created["product_id"] == "PROD-TEST-001"
    assert created["minimum_temperature"] < created["maximum_temperature"]

def test_tc02_invalid_product_temperature_range():
    """TC02: Invalid product temperature range (min >= max) must be rejected."""
    invalid_prod = {
        "product_id": "PROD-INV-001",
        "product_name": "Invalid Temperature Drug",
        "minimum_temperature": 10.0,
        "maximum_temperature": 4.0
    }
    with pytest.raises(ValueError) as excinfo:
        ProductService.create(invalid_prod)
    assert "Invalid temperature range" in str(excinfo.value)

def test_tc03_lot_creation(client):
    """TC03: Valid lot creation linked to product."""
    payload = {
        "lot_id": "LOT-2026-TEST01",
        "product_id": "PROD-001",
        "supplier_name": "BioPharma Labs",
        "manufacturing_date": "2026-01-01T00:00:00Z",
        "expiry_date": "2026-12-31T00:00:00Z",
        "quantity": 10000,
        "unit": "DOSES"
    }
    res = client.post("/api/v1/lots", json=payload)
    assert res.status_code == 201
    assert res.get_json()["data"]["lot_id"] == "LOT-2026-TEST01"

def test_tc04_invalid_lot_product_relationship(client):
    """TC04: Lot referencing non-existent product must fail."""
    payload = {
        "lot_id": "LOT-INV-001",
        "product_id": "PROD-NONEXISTENT-999",
        "supplier_name": "Pharma Test",
        "manufacturing_date": "2026-01-01T00:00:00Z",
        "expiry_date": "2026-12-31T00:00:00Z",
        "quantity": 5000
    }
    res = client.post("/api/v1/lots", json=payload)
    assert res.status_code == 422
    assert res.get_json()["error_code"] == "INVALID_PRODUCT_REFERENCE"

def test_tc05_shipment_creation(client):
    """TC05: Valid shipment creation."""
    payload = {
        "shipment_id": "SHP-2026-TEST01",
        "lot_id": "LOT-2026-TEST01",
        "product_id": "PROD-001",
        "packaging_id": "PKG-002",
        "origin": "Boston, MA",
        "destination": "Basel, CH",
        "carrier_name": "FedEx ColdChain Direct",
        "planned_departure": "2026-02-01T08:00:00Z",
        "expected_arrival": "2026-02-02T16:00:00Z"
    }
    res = client.post("/api/v1/shipments", json=payload)
    assert res.status_code == 201
    assert res.get_json()["data"]["shipment_id"] == "SHP-2026-TEST01"

def test_tc06_invalid_shipment_lot_relationship(client):
    """TC06: Shipment referencing lot belonging to another product must be rejected."""
    payload = {
        "shipment_id": "SHP-2026-INV01",
        "lot_id": "LOT-2026-TEST01", # belongs to PROD-001
        "product_id": "PROD-002",    # mismatched!
        "packaging_id": "PKG-001",
        "origin": "Boston, MA",
        "destination": "London, UK",
        "carrier_name": "DHL Express",
        "planned_departure": "2026-02-01T08:00:00Z",
        "expected_arrival": "2026-02-02T16:00:00Z"
    }
    res = client.post("/api/v1/shipments", json=payload)
    assert res.status_code == 422
    assert res.get_json()["error_code"] == "LOT_PRODUCT_MISMATCH"

def test_tc07_packaging_compatibility(client):
    """TC07: Check packaging compatibility endpoint."""
    res = client.get("/api/v1/packaging/PKG-001/compatibility")
    assert res.status_code == 200
    assert isinstance(res.get_json()["data"], list)

def test_tc08_logger_assignment():
    """TC08: Assign logger to shipment and check active state."""
    logger_id = "LOG-2026-TEST01"
    supabase.table("loggers").insert({
        "logger_id": logger_id,
        "serial_number": "SN-TEST-001",
        "model": "SenseAware 4G",
        "calibration_date": "2026-01-01T00:00:00Z",
        "calibration_expiry": "2026-12-31T00:00:00Z",
        "accuracy_tolerance": 0.50,
        "measurement_uncertainty": 0.20
    }, upsert=True).execute()

    asg = LoggerService.assign_to_shipment(logger_id, "SHP-2026-TEST01")
    assert asg["logger_id"] == logger_id
    assert asg["shipment_id"] == "SHP-2026-TEST01"
    assert asg["status"] == "ACTIVE"
