# backend/app/routes/shipment_routes.py
from flask import Blueprint, request
from app.services.shipment_service import ShipmentService
from app.services.temperature_service import TemperatureService
from app.services.custody_service import CustodyService
from app.services.compliance_service import ComplianceService
from app.config.supabase_client import supabase
from app.utils.response import success_response, error_response

shipment_bp = Blueprint("shipments", __name__)

@shipment_bp.route("", methods=["GET"])
def get_shipments():
    status = request.args.get("status")
    compliance = request.args.get("compliance")
    product_id = request.args.get("product_id")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 25))

    data = ShipmentService.get_all(status=status, compliance=compliance, product_id=product_id, page=page, page_size=page_size)
    return success_response(data=data["items"], meta={"total": data["total"], "page": page, "page_size": page_size}, message="Shipments retrieved successfully")

@shipment_bp.route("", methods=["POST"])
def create_shipment():
    data = request.get_json() or {}
    lot_id = data.get("lot_id")
    product_id = data.get("product_id")
    packaging_id = data.get("packaging_id")

    # Validate lot belongs to product
    lots = supabase.table("lots").select("*").eq("lot_id", lot_id).execute().data
    if not lots:
        return error_response(f"Lot '{lot_id}' not found", error_code="INVALID_LOT", status_code=422)
    if lots[0]["product_id"] != product_id:
        return error_response(f"Lot '{lot_id}' belongs to product '{lots[0]['product_id']}', not '{product_id}'", error_code="LOT_PRODUCT_MISMATCH", status_code=422)

    # Validate packaging
    pkgs = supabase.table("packaging").select("*").eq("packaging_id", packaging_id).execute().data
    if not pkgs:
        return error_response(f"Packaging '{packaging_id}' not found", error_code="INVALID_PACKAGING", status_code=422)

    created = ShipmentService.create(data)
    return success_response(data=created, message="Shipment created successfully", status_code=201)

@shipment_bp.route("/<shipment_id>", methods=["GET"])
def get_shipment(shipment_id):
    shipment = ShipmentService.get_by_id(shipment_id)
    if not shipment:
        return error_response("Shipment not found", error_code="SHIPMENT_NOT_FOUND", status_code=404)
    return success_response(data=shipment, message="Shipment retrieved successfully")

@shipment_bp.route("/<shipment_id>", methods=["PUT"])
def update_shipment(shipment_id):
    data = request.get_json() or {}
    updated = ShipmentService.update(shipment_id, data)
    if not updated:
        return error_response("Shipment not found", error_code="SHIPMENT_NOT_FOUND", status_code=404)
    return success_response(data=updated, message="Shipment updated successfully")

@shipment_bp.route("/<shipment_id>/timeline", methods=["GET"])
def get_shipment_timeline(shipment_id):
    bundle = ShipmentService.get_shipment_details_bundle(shipment_id)
    if not bundle:
        return error_response("Shipment not found", error_code="SHIPMENT_NOT_FOUND", status_code=404)
    return success_response(data=bundle, message="Shipment full timeline bundle retrieved")

@shipment_bp.route("/<shipment_id>/temperature", methods=["GET"])
def get_shipment_temperature(shipment_id):
    trends = TemperatureService.get_shipment_trends(shipment_id)
    return success_response(data=trends, message="Shipment temperature readings retrieved")

@shipment_bp.route("/<shipment_id>/custody", methods=["GET"])
def get_shipment_custody(shipment_id):
    timeline = CustodyService.get_shipment_timeline(shipment_id)
    gaps = CustodyService.detect_custody_gaps(shipment_id)
    return success_response(data={"timeline": timeline, "analysis": gaps}, message="Shipment custody records retrieved")

@shipment_bp.route("/<shipment_id>/route", methods=["GET"])
def get_shipment_route(shipment_id):
    stops = supabase.table("route_stops").select("*").eq("shipment_id", shipment_id).order("stop_sequence", desc=False).execute().data
    return success_response(data=stops, message="Shipment route stops retrieved")

@shipment_bp.route("/<shipment_id>/excursions", methods=["GET"])
def get_shipment_excursions(shipment_id):
    excursions = supabase.table("excursion_reports").select("*").eq("shipment_id", shipment_id).order("start_timestamp", desc=True).execute().data
    return success_response(data=excursions, message="Shipment excursions retrieved")

@shipment_bp.route("/<shipment_id>/compliance", methods=["GET"])
def get_shipment_compliance(shipment_id):
    report = ComplianceService.get_report_for_shipment(shipment_id)
    if not report:
        # Run compliance engine on demand
        try:
            report = ComplianceService.analyze_shipment_compliance(shipment_id)
        except Exception as e:
            return error_response(str(e), error_code="COMPLIANCE_ANALYSIS_FAILED", status_code=400)
    return success_response(data=report, message="Shipment compliance report retrieved")
