# backend/app/routes/logger_routes.py
from flask import Blueprint, request
from app.services.logger_service import LoggerService
from app.utils.response import success_response, error_response

logger_bp = Blueprint("loggers", __name__)

@logger_bp.route("", methods=["GET"])
def get_loggers():
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 50))
    data = LoggerService.get_all(status=status, page=page, page_size=page_size)
    return success_response(data=data["items"], meta={"total": data["total"], "page": page, "page_size": page_size}, message="Loggers retrieved successfully")

@logger_bp.route("", methods=["POST"])
def create_logger():
    data = request.get_json() or {}
    try:
        created = LoggerService.create(data)
        return success_response(data=created, message="Logger registered successfully", status_code=201)
    except ValueError as e:
        return error_response(str(e), error_code="INVALID_CALIBRATION_DATES", status_code=422)

@logger_bp.route("/<logger_id>", methods=["GET"])
def get_logger(logger_id):
    logger = LoggerService.get_by_id(logger_id)
    if not logger:
        return error_response("Logger not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=logger, message="Logger retrieved")

@logger_bp.route("/<logger_id>", methods=["PUT"])
def update_logger(logger_id):
    data = request.get_json() or {}
    updated = LoggerService.update(logger_id, data)
    if not updated:
        return error_response("Logger not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=updated, message="Logger updated")

@logger_bp.route("/<logger_id>/assign", methods=["POST"])
def assign_logger(logger_id):
    data = request.get_json() or {}
    shipment_id = data.get("shipment_id")
    assigned_at = data.get("assigned_at")
    if not shipment_id:
        return error_response("Shipment ID is required for assignment", error_code="MISSING_PARAM", status_code=400)
    
    asg = LoggerService.assign_to_shipment(logger_id, shipment_id, assigned_at)
    return success_response(data=asg, message="Logger assigned to shipment successfully")

@logger_bp.route("/<logger_id>/assignments", methods=["GET"])
def get_logger_assignments(logger_id):
    asgs = LoggerService.get_assignments(logger_id)
    return success_response(data=asgs, message="Logger assignment history retrieved")

@logger_bp.route("/<logger_id>/calibration", methods=["GET"])
def get_logger_calibration(logger_id):
    check = LoggerService.validate_calibration(logger_id)
    return success_response(data=check, message="Logger calibration validated")
