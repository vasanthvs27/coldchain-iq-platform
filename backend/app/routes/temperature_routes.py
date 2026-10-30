# backend/app/routes/temperature_routes.py
from flask import Blueprint, request
from app.services.temperature_service import TemperatureService
from app.services.excursion_service import ExcursionService
from app.utils.response import success_response, error_response

temp_bp = Blueprint("temperature", __name__)

@temp_bp.route("/readings", methods=["GET"])
def get_readings():
    shipment_id = request.args.get("shipment_id")
    logger_id = request.args.get("logger_id")
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 100))

    data = TemperatureService.get_readings(shipment_id=shipment_id, logger_id=logger_id, status=status, page=page, page_size=page_size)
    return success_response(data=data["items"], meta={"total": data["total"], "page": page, "page_size": page_size}, message="Temperature readings retrieved")

@temp_bp.route("/readings", methods=["POST"])
def insert_reading():
    data = request.get_json() or {}
    try:
        created = TemperatureService.insert_reading(data)
        return success_response(data=created, message="Temperature reading ingested", status_code=201)
    except Exception as e:
        return error_response(str(e), error_code="INGESTION_ERROR", status_code=400)

@temp_bp.route("/readings/<reading_id>", methods=["GET"])
def get_reading(reading_id):
    reading = TemperatureService.get_by_id(reading_id)
    if not reading:
        return error_response("Reading not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=reading, message="Reading retrieved")

@temp_bp.route("/shipments/<shipment_id>/trends", methods=["GET"])
def get_trends(shipment_id):
    trends = TemperatureService.get_shipment_trends(shipment_id)
    return success_response(data=trends, message="Temperature trends retrieved")

@temp_bp.route("/shipments/<shipment_id>/gaps", methods=["GET"])
def get_gaps(shipment_id):
    interval = int(request.args.get("interval_minutes", 10))
    gaps = TemperatureService.detect_missing_gaps(shipment_id, expected_interval_minutes=interval)
    return success_response(data=gaps, message="Missing temperature gaps analysis retrieved")

@temp_bp.route("/excursions", methods=["GET"])
def get_temperature_excursions():
    shipment_id = request.args.get("shipment_id")
    severity = request.args.get("severity")
    data = ExcursionService.get_all(shipment_id=shipment_id, severity=severity)
    return success_response(data=data["items"], meta={"total": data["total"]}, message="Excursions retrieved")

@temp_bp.route("/analyze", methods=["POST"])
def analyze_temperature():
    data = request.get_json() or {}
    shipment_id = data.get("shipment_id")
    if not shipment_id:
        return error_response("Shipment ID is required", error_code="MISSING_SHIPMENT", status_code=400)
    
    excursions = ExcursionService.analyze_shipment_excursions(shipment_id)
    return success_response(data=excursions, message="Temperature excursion analysis complete")
