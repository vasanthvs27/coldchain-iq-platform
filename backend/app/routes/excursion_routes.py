# backend/app/routes/excursion_routes.py
from flask import Blueprint, request
from app.services.excursion_service import ExcursionService
from app.utils.response import success_response, error_response

excursion_bp = Blueprint("excursions", __name__)

@excursion_bp.route("", methods=["GET"])
def get_excursions():
    shipment_id = request.args.get("shipment_id")
    severity = request.args.get("severity")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 50))
    data = ExcursionService.get_all(shipment_id=shipment_id, severity=severity, page=page, page_size=page_size)
    return success_response(data=data["items"], meta={"total": data["total"], "page": page, "page_size": page_size}, message="Excursion reports retrieved")

@excursion_bp.route("/analyze", methods=["POST"])
def analyze_excursions():
    data = request.get_json() or {}
    shipment_id = data.get("shipment_id")
    if not shipment_id:
        return error_response("Shipment ID is required", error_code="MISSING_PARAM", status_code=400)
    
    excursions = ExcursionService.analyze_shipment_excursions(shipment_id)
    return success_response(data=excursions, message="Shipment excursions calculated")

@excursion_bp.route("/<excursion_id>", methods=["GET"])
def get_excursion(excursion_id):
    excr = ExcursionService.get_by_id(excursion_id)
    if not excr:
        return error_response("Excursion not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=excr, message="Excursion retrieved")

@excursion_bp.route("/<excursion_id>/investigation", methods=["PUT"])
def update_investigation(excursion_id):
    data = request.get_json() or {}
    updated = ExcursionService.update_investigation(excursion_id, data)
    if not updated:
        return error_response("Excursion not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=updated, message="Excursion investigation record updated")

@excursion_bp.route("/<excursion_id>/evidence", methods=["GET"])
def get_excursion_evidence(excursion_id):
    excr = ExcursionService.get_by_id(excursion_id)
    if not excr:
        return error_response("Excursion not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data={
        "excursion_id": excr["excursion_id"],
        "shipment_id": excr["shipment_id"],
        "evidence_reference": excr.get("evidence_reference"),
        "severity": excr.get("severity"),
        "duration_minutes": excr.get("calculated_duration"),
        "temperature_bounds": [excr.get("minimum_observed_temperature"), excr.get("maximum_observed_temperature")]
    }, message="Excursion forensic evidence retrieved")
