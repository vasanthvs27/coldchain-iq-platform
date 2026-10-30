# backend/app/routes/custody_routes.py
from flask import Blueprint, request
from app.services.custody_service import CustodyService
from app.utils.response import success_response, error_response

custody_bp = Blueprint("custody", __name__)

@custody_bp.route("", methods=["GET"])
def get_custody_events():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 50))
    data = CustodyService.get_all(page=page, page_size=page_size)
    return success_response(data=data["items"], meta={"total": data["total"], "page": page, "page_size": page_size}, message="Custody events retrieved")

@custody_bp.route("", methods=["POST"])
def create_custody_event():
    data = request.get_json() or {}
    try:
        created = CustodyService.create(data)
        return success_response(data=created, message="Custody event recorded", status_code=201)
    except Exception as e:
        return error_response(str(e), error_code="RECORDING_ERROR", status_code=400)

@custody_bp.route("/<event_id>", methods=["GET"])
def get_custody_event(event_id):
    ev = CustodyService.get_by_id(event_id)
    if not ev:
        return error_response("Custody event not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=ev, message="Custody event retrieved")

@custody_bp.route("/shipments/<shipment_id>/timeline", methods=["GET"])
def get_shipment_custody_timeline(shipment_id):
    timeline = CustodyService.get_shipment_timeline(shipment_id)
    return success_response(data=timeline, message="Custody timeline retrieved")

@custody_bp.route("/shipments/<shipment_id>/gaps", methods=["GET"])
def get_custody_gaps(shipment_id):
    gaps = CustodyService.detect_custody_gaps(shipment_id)
    return success_response(data=gaps, message="Custody gap verification complete")
