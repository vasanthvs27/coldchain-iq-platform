# backend/app/routes/reproducibility_routes.py
from flask import Blueprint, request
from app.services.reproducibility_service import ReproducibilityService
from app.services.export_service import ExportService
from app.utils.response import success_response, error_response

reproducibility_bp = Blueprint("reproducibility", __name__)

@reproducibility_bp.route("/run", methods=["POST"])
def run_reproducibility():
    data = request.get_json() or {}
    seed = int(data.get("seed", 20261022))
    sample_count = int(data.get("sample_count", 20))
    try:
        report = ReproducibilityService.verify_reproducibility(seed=seed, sample_count=sample_count)
        return success_response(data=report, message="Deterministic reproducibility verification completed")
    except Exception as e:
        return error_response(str(e), error_code="REPRODUCIBILITY_FAILED", status_code=500)

@reproducibility_bp.route("/results", methods=["GET"])
def get_reproducibility_results():
    report = ReproducibilityService.verify_reproducibility()
    return success_response(data=report, message="Reproducibility verification summary retrieved")

@reproducibility_bp.route("/export", methods=["POST"])
def export_datasets():
    try:
        res = ExportService.export_all_datasets()
        return success_response(data=res, message="All datasets exported to CSV, JSON, SQL with manifest.json")
    except Exception as e:
        return error_response(str(e), error_code="EXPORT_FAILED", status_code=500)
