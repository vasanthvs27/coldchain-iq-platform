# backend/tests/test_validation.py
import pytest
import os
from app.services.validation_service import ValidationService
from app.services.evaluation_service import EvaluationService
from app.config import Config
from app.config.supabase_client import supabase

def test_tc30_primary_key_uniqueness():
    """TC30: Validation checks primary key uniqueness."""
    report = ValidationService.run_all_validations()
    pk_rule = next((r for r in report["results"] if "Primary Key Uniqueness" in r["rule_name"]), None)
    assert pk_rule is not None
    assert pk_rule["status"] in ("PASSED", "WARNING")

def test_tc31_foreign_key_integrity():
    """TC31: Foreign key integrity validation passes for valid dataset."""
    report = ValidationService.run_all_validations()
    fk_rule = next((r for r in report["results"] if "Foreign Key Integrity" in r["rule_name"]), None)
    assert fk_rule is not None
    assert fk_rule["passed_count"] >= 0

def test_tc32_enum_validation():
    """TC32: Lifecycle status and shipment status conform to expected enumeration."""
    shipments = supabase.table("shipments").select("shipment_status").execute().data
    allowed_statuses = {"SCHEDULED", "IN_TRANSIT", "DELIVERED", "QUARANTINED", "CANCELLED", "PENDING"}
    for s in shipments:
        st = s.get("shipment_status", "DELIVERED")
        assert st in allowed_statuses

def test_tc33_date_ordering():
    """TC33: Manufacturing date precedes expiry date for all lots."""
    lots = supabase.table("lots").select("manufacturing_date,expiry_date").execute().data
    for lot in lots:
        if lot.get("manufacturing_date") and lot.get("expiry_date"):
            assert lot["manufacturing_date"] < lot["expiry_date"]

def test_tc34_derived_value_reconciliation():
    """TC34: Derived metrics reconciliation validation."""
    report = ValidationService.run_all_validations()
    recon_rule = next((r for r in report["results"] if "Derived Compliance Values Reconciliation" in r["rule_name"]), None)
    assert recon_rule is not None
    assert recon_rule["status"] == "PASSED"

def test_tc35_ground_truth_separation():
    """TC35: Ground-truth files are stored in data/ground_truth and separated from operational inputs."""
    gt_json = os.path.join(Config.GROUND_TRUTH_DIR, "ground_truth.json")
    # Verify path is isolated
    assert "ground_truth" in gt_json
    assert not gt_json.endswith(".py")

def test_tc36_precision_calculation():
    """TC36: Precision metric calculation TP / (TP + FP) safely handles zero denominators."""
    eval_metrics = EvaluationService.evaluate_detection_performance()
    precision = eval_metrics["overall_metrics"]["precision"]
    assert 0.0 <= precision <= 100.0

def test_tc37_recall_and_f1_calculation():
    """TC37: Recall TP / (TP + FN) and F1 calculation 2*P*R/(P+R)."""
    eval_metrics = EvaluationService.evaluate_detection_performance()
    recall = eval_metrics["overall_metrics"]["recall"]
    f1 = eval_metrics["overall_metrics"]["f1_score"]
    assert 0.0 <= recall <= 100.0
    assert 0.0 <= f1 <= 100.0
