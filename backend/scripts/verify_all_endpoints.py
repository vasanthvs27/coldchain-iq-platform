import os
import sys
import json
import time

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app

app = create_app()
client = app.test_client()

endpoints = [
    ("GET", "/api/v1/health", "Health Check"),
    ("GET", "/api/v1/dashboard/overview", "Executive Dashboard Overview"),
    ("GET", "/api/v1/dashboard/compliance-summary", "Dashboard Compliance Breakdown"),
    ("GET", "/api/v1/dashboard/excursion-summary", "Dashboard Excursion Summary"),
    ("GET", "/api/v1/dashboard/shipment-trends", "Dashboard Shipment Trends"),
    ("GET", "/api/v1/dashboard/temperature-trends", "Dashboard Temperature Trends"),
    ("GET", "/api/v1/products", "Product Master Catalog"),
    ("GET", "/api/v1/products/PROD-001", "Product Detail PROD-001"),
    ("GET", "/api/v1/products/PROD-001/lots", "Product Lots"),
    ("GET", "/api/v1/products/PROD-001/policies", "Product Policies"),
    ("GET", "/api/v1/lots", "Lots & Batches"),
    ("GET", "/api/v1/packaging", "Packaging Profiles"),
    ("GET", "/api/v1/loggers", "Logger Fleet"),
    ("GET", "/api/v1/shipments", "Shipments List"),
    ("GET", "/api/v1/custody", "Chain of Custody Events"),
    ("GET", "/api/v1/policies", "Threshold Policies"),
    ("GET", "/api/v1/excursions", "Temperature Excursions"),
    ("GET", "/api/v1/compliance/reports", "Compliance Reports"),
    ("GET", "/api/v1/analytics/overview", "Analytics Overview"),
    ("GET", "/api/v1/analytics/temperature", "Analytics Temperature"),
    ("GET", "/api/v1/analytics/excursions", "Analytics Excursions"),
    ("GET", "/api/v1/analytics/compliance", "Analytics Compliance"),
    ("GET", "/api/v1/analytics/carriers", "Analytics Carrier Risk"),
    ("GET", "/api/v1/analytics/routes", "Analytics Routes Dwell"),
    ("GET", "/api/v1/analytics/risk", "Analytics Risk Matrix"),
    ("GET", "/api/v1/validation/summary", "Data Validation Summary"),
    ("GET", "/api/v1/evaluation/metrics", "Ground Truth Evaluation Metrics"),
    ("GET", "/api/v1/evaluation/confusion-matrix", "Confusion Matrix"),
    ("GET", "/api/v1/evaluation/anomaly-breakdown", "Anomaly Breakdown"),
    ("GET", "/api/v1/reproducibility/results", "Reproducibility Results"),
    ("GET", "/api/v1/audit/events", "Audit Trail Events"),
]

print("=" * 85)
print(f"{'Endpoint':<45} | {'Result':<8} | {'HTTP':<5} | {'Duration':<8} | {'Details'}")
print("=" * 85)

passed = 0
failed = 0

for method, path, desc in endpoints:
    start_t = time.time()
    try:
        if method == "GET":
            res = client.get(path)
        dur = f"{(time.time() - start_t)*1000:.1f}ms"
        status_code = res.status_code
        data = res.get_json() or {}
        success = data.get("success", False)
        
        if status_code == 200 and success:
            print(f"{path:<45} | {'PASS':<8} | {status_code:<5} | {dur:<8} | {desc}", flush=True)
            passed += 1
        else:
            print(f"{path:<45} | {'FAIL':<8} | {status_code:<5} | {dur:<8} | Success={success} ({desc})", flush=True)
            failed += 1
    except Exception as e:
        dur = f"{(time.time() - start_t)*1000:.1f}ms"
        print(f"{path:<45} | {'ERROR':<8} | {'ERR':<5} | {dur:<8} | {str(e)}", flush=True)
        failed += 1

# Dynamic shipment sub-resource test
try:
    ship_res = client.get("/api/v1/shipments").get_json() or {}
    shipments = ship_res.get("data", [])
    if shipments:
        shp_id = shipments[0]["shipment_id"]
        sub_tests = [
            (f"/api/v1/shipments/{shp_id}", f"Shipment Detail {shp_id}"),
            (f"/api/v1/shipments/{shp_id}/timeline", f"Shipment Timeline"),
            (f"/api/v1/shipments/{shp_id}/temperature", f"Shipment Temperature Readings"),
            (f"/api/v1/shipments/{shp_id}/route", f"Shipment Route & Stops"),
            (f"/api/v1/shipments/{shp_id}/custody", f"Shipment Custody Events"),
            (f"/api/v1/shipments/{shp_id}/compliance", f"Shipment Compliance Evaluation"),
        ]
        for path, desc in sub_tests:
            start_t = time.time()
            res = client.get(path)
            dur = f"{(time.time() - start_t)*1000:.1f}ms"
            data = res.get_json() or {}
            if res.status_code == 200 and data.get("success"):
                print(f"{path:<45} | {'PASS':<8} | {res.status_code:<5} | {dur:<8} | {desc}", flush=True)
                passed += 1
            else:
                print(f"{path:<45} | {'FAIL':<8} | {res.status_code:<5} | {dur:<8} | {desc}", flush=True)
                failed += 1
except Exception as e:
    print(f"Error checking shipment sub-resources: {e}")

print("=" * 85)
print(f"COMPLETE AUDIT RESULT: {passed} PASSED, {failed} FAILED out of {passed + failed} ENDPOINTS TESTED.")
print("=" * 85)

sys.exit(0 if failed == 0 else 1)
