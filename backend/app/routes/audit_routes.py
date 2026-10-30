# backend/app/routes/audit_routes.py
from flask import Blueprint, request
from app.config.supabase_client import supabase
from app.utils.response import success_response

audit_bp = Blueprint("audit", __name__)

@audit_bp.route("/events", methods=["GET"])
def get_audit_events():
    entity_type = request.args.get("entity_type")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 50))
    offset = (page - 1) * page_size

    query = supabase.table("audit_events").select("*")
    if entity_type:
        query = query.eq("entity_type", entity_type)

    res = query.order("created_at", desc=True).offset(offset).limit(page_size).execute()
    count_res = supabase.table("audit_events").select("event_id").execute()
    total = count_res.count or len(count_res.data)

    return success_response(data=res.data, meta={"total": total, "page": page, "page_size": page_size}, message="Audit events retrieved")

@audit_bp.route("/shipments/<shipment_id>", methods=["GET"])
def get_shipment_audit_history(shipment_id):
    res = supabase.table("audit_events").select("*").eq("entity_type", "shipment").eq("entity_id", shipment_id).order("created_at", desc=True).execute()
    return success_response(data=res.data, message="Shipment audit events retrieved")
