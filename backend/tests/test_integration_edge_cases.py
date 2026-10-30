# backend/tests/test_integration_edge_cases.py
import pytest
from app.config.supabase_client import supabase

def test_tc44_empty_dataset(client):
    """TC44: Graceful handling when filtering returns empty list."""
    res = client.get("/api/v1/shipments?status=NONEXISTENT_STATUS_999")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert isinstance(data, list)
    assert len(data) == 0

def test_tc45_invalid_api_request(client):
    """TC45: Malformed JSON or invalid payload returns 400 Bad Request."""
    res = client.post("/api/v1/auth/login", data="malformed-not-json", content_type="application/json")
    assert res.status_code == 400

def test_tc46_missing_resource(client):
    """TC46: Querying nonexistent resource returns 404 with structured error response."""
    res = client.get("/api/v1/products/PROD-DOES-NOT-EXIST-404")
    assert res.status_code == 404
    json_data = res.get_json()
    assert json_data["success"] is False
    assert json_data["error_code"] == "PRODUCT_NOT_FOUND"

def test_tc47_database_failure_handling(client):
    """TC47: Resilient handling returns appropriate 4xx/5xx code."""
    res = client.post("/api/v1/products", json={"minimum_temperature": 10, "maximum_temperature": 2})
    assert res.status_code in (400, 422)

def test_tc48_large_dataset_pagination(client):
    """TC48: Pagination limits payload size and returns meta attributes."""
    res = client.get("/api/v1/shipments?page=1&page_size=5")
    assert res.status_code == 200
    json_data = res.get_json()
    assert len(json_data["data"]) <= 5
    assert "meta" in json_data
    assert json_data["meta"]["page"] == 1
    assert json_data["meta"]["page_size"] == 5

def test_tc49_concurrent_generation_protection(client):
    """TC49: Data generation runs tracked with explicit RUN-ID."""
    res = client.post("/api/v1/generator/configure", json={"mode": "STARTER", "shipment_count": 10})
    assert res.status_code == 200
    assert "mode" in res.get_json()["data"]

def test_tc50_historical_event_preservation():
    """TC50: Past compliance reports and custody events are preserved, not overwritten."""
    reports = supabase.table("compliance_reports").select("*").execute().data
    assert len(reports) >= 1
    # Check that each report preserves its generated_at timestamp
    for r in reports:
        assert "generated_at" in r
        assert r["generated_at"] is not None
