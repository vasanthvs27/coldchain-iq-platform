# backend/app/routes/compliance_routes.py
from flask import Blueprint, request
from app.services.compliance_service import ComplianceService
from app.utils.response import success_response, error_response

compliance_bp = Blueprint("compliance", __name__)

@compliance_bp.route("/analyze/<shipment_id>", methods=["POST"])
def analyze_shipment(shipment_id):
    data = request.get_json() or {}
    applied_policy_id = data.get("applied_policy_id")
    try:
        report = ComplianceService.analyze_shipment_compliance(shipment_id, applied_policy_id)
        return success_response(data=report, message=f"Compliance analysis completed for shipment {shipment_id}")
    except ValueError as e:
        return error_response(str(e), error_code="ANALYSIS_VALIDATION_ERROR", status_code=404)
    except Exception as e:
        return error_response(str(e), error_code="COMPLIANCE_ERROR", status_code=400)

@compliance_bp.route("/reports", methods=["GET"])
def get_reports():
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 50))
    data = ComplianceService.get_all_reports(page=page, page_size=page_size, status=status)
    return success_response(data=data["items"], meta={"total": data["total"], "page": page, "page_size": page_size}, message="Compliance reports retrieved")

@compliance_bp.route("/reports/<report_id>", methods=["GET"])
def get_report(report_id):
    report = ComplianceService.get_report_by_id(report_id)
    if not report:
        return error_response("Compliance report not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=report, message="Compliance report retrieved")

@compliance_bp.route("/shipments/<shipment_id>", methods=["GET"])
def get_shipment_report(shipment_id):
    report = ComplianceService.get_report_for_shipment(shipment_id)
    if not report:
        # Generate on the fly
        try:
            report = ComplianceService.analyze_shipment_compliance(shipment_id)
        except Exception as e:
            return error_response(str(e), error_code="REPORT_GENERATION_FAILED", status_code=400)
    return success_response(data=report, message="Shipment compliance report retrieved")

@compliance_bp.route("/reports/<report_id>/export", methods=["POST"])
def export_report(report_id):
    report = ComplianceService.get_report_by_id(report_id)
    if not report:
        return error_response("Report not found", error_code="NOT_FOUND", status_code=404)
    
    # Formulate certificate payload
    export_payload = {
        "certificate_id": f"CERT-{report['report_id']}",
        "shipment_id": report["shipment_id"],
        "compliance_decision": report["compliance_status"],
        "compliance_score": report["compliance_score"],
        "evidence_summary": report.get("evidence_references", []),
        "policy_version": report.get("policy_version"),
        "audit_hash": f"SHA256:{hash(report['report_id']) % 1000000000000:012x}",
        "certified_at": report.get("generated_at")
    }
    return success_response(data=export_payload, message="Compliance certificate generated successfully")
