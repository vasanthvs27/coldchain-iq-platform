# backend/app/routes/lot_routes.py
from flask import Blueprint, request
from datetime import datetime, timezone
from app.config.supabase_client import supabase
from app.utils.response import success_response, error_response

lot_bp = Blueprint("lots", __name__)

@lot_bp.route("", methods=["GET"])
def get_lots():
    product_id = request.args.get("product_id")
    status = request.args.get("status")
    query = supabase.table("lots").select("*")
    if product_id:
        query = query.eq("product_id", product_id)
    if status:
        query = query.eq("lifecycle_status", status)
    
    lots = query.order("manufacturing_date", desc=True).execute().data
    return success_response(data=lots, meta={"total": len(lots)}, message="Lots retrieved successfully")

@lot_bp.route("", methods=["POST"])
def create_lot():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    
    # Validate product exists
    prods = supabase.table("products").select("product_id").eq("product_id", product_id).execute().data
    if not prods:
        return error_response(f"Product '{product_id}' does not exist", error_code="INVALID_PRODUCT_REFERENCE", status_code=422)

    # Validate dates
    mfg_date = data.get("manufacturing_date")
    exp_date = data.get("expiry_date")
    if mfg_date and exp_date and mfg_date >= exp_date:
        return error_response("Manufacturing date must precede expiry date", error_code="INVALID_DATE_SEQUENCE", status_code=422)

    if not data.get("created_at"):
        data["created_at"] = datetime.now(timezone.utc).isoformat()
    if not data.get("lifecycle_status"):
        data["lifecycle_status"] = "RELEASED"

    res = supabase.table("lots").insert(data).execute()
    return success_response(data=res.data[0] if res.data else data, message="Lot created successfully", status_code=201)

@lot_bp.route("/<lot_id>", methods=["GET"])
def get_lot(lot_id):
    res = supabase.table("lots").select("*").eq("lot_id", lot_id).execute()
    if not res.data:
        return error_response("Lot not found", error_code="LOT_NOT_FOUND", status_code=404)
    return success_response(data=res.data[0], message="Lot retrieved successfully")

@lot_bp.route("/<lot_id>", methods=["PUT"])
def update_lot(lot_id):
    data = request.get_json() or {}
    res = supabase.table("lots").update(data).eq("lot_id", lot_id).execute()
    if not res.data:
        return error_response("Lot not found", error_code="LOT_NOT_FOUND", status_code=404)
    return success_response(data=res.data[0], message="Lot updated successfully")

@lot_bp.route("/<lot_id>/shipments", methods=["GET"])
def get_lot_shipments(lot_id):
    res = supabase.table("shipments").select("*").eq("lot_id", lot_id).order("planned_departure", desc=True).execute()
    return success_response(data=res.data, message="Lot shipments retrieved successfully")
