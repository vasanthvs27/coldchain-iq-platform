# backend/app/routes/route_routes.py
from flask import Blueprint, request
from app.config.supabase_client import supabase
from app.utils.response import success_response, error_response

route_bp = Blueprint("routes", __name__)

@route_bp.route("/<shipment_id>", methods=["GET"])
def get_shipment_route(shipment_id):
    stops = supabase.table("route_stops").select("*").eq("shipment_id", shipment_id).order("stop_sequence", desc=False).execute().data
    return success_response(data=stops, message="Shipment route stops retrieved")

@route_bp.route("/stops", methods=["POST"])
def create_stop():
    data = request.get_json() or {}
    # auto calculate dwell if actual arrival and departure provided
    arr = data.get("actual_arrival")
    dep = data.get("departure_time")
    if arr and dep and not data.get("dwell_duration"):
        from datetime import datetime
        t1 = datetime.fromisoformat(arr.replace("Z", "+00:00"))
        t2 = datetime.fromisoformat(dep.replace("Z", "+00:00"))
        data["dwell_duration"] = max(0, int((t2 - t1).total_seconds() / 60))

    res = supabase.table("route_stops").insert(data).execute()
    return success_response(data=res.data[0] if res.data else data, message="Route stop logged", status_code=201)

@route_bp.route("/stops/<stop_id>", methods=["GET"])
def get_stop(stop_id):
    res = supabase.table("route_stops").select("*").eq("route_stop_id", stop_id).execute()
    if not res.data:
        return error_response("Route stop not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=res.data[0], message="Route stop retrieved")

@route_bp.route("/stops/<stop_id>", methods=["PUT"])
def update_stop(stop_id):
    data = request.get_json() or {}
    res = supabase.table("route_stops").update(data).eq("route_stop_id", stop_id).execute()
    if not res.data:
        return error_response("Route stop not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=res.data[0], message="Route stop updated")
