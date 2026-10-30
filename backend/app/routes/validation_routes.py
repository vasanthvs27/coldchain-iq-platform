# backend/app/routes/validation_routes.py
from flask import Blueprint
from app.services.validation_service import ValidationService
from app.utils.response import success_response, error_response

validation_bp = Blueprint("validation", __name__)

@validation_bp.route("/run", methods=["POST"])
def run_validations():
    try:
        report = ValidationService.run_all_validations()
        return success_response(data=report, message="Comprehensive data validation completed")
    except Exception as e:
        return error_response(str(e), error_code="VALIDATION_EXECUTION_ERROR", status_code=500)

@validation_bp.route("/results", methods=["GET"])
def get_validation_results():
    summary = ValidationService.get_summary()
    return success_response(data=summary["recent_results"], meta={"count": summary["count"]}, message="Validation results retrieved")

@validation_bp.route("/summary", methods=["GET"])
def get_validation_summary():
    report = ValidationService.run_all_validations()
    return success_response(data=report["summary"], message="Validation summary retrieved")
